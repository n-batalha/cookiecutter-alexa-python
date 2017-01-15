import alexandra
import logging

from utils import App

replacements = {
    "lemon": "kaffir lime leaves",
    "anise seed": "cardamom",
    "beer": "1 cup water, white grape juice, apple cider or apple juice, diluted peach or apricot syrups",
}

app = App()
wsgi_app = app.create_wsgi_app()
logger = logging.getLogger(__name__)


@app.launch
def launch_handler(session):
    return alexandra.reprompt('Which ingredient would you like to replace?')


@app.intent('FindReplacement')
def find_ingredient_replacement(slots, session):
    try:
        ingredient = slots['ingredient']
    except KeyError:
        # when doing proper logging, we should move `slots` to the extra param of the logger
        logger.error(("Alexa does not recognize 'Ingredient' in the slots"
                      ". Slots available are {}. Session is {}").format(slots, session))

    if ingredient in replacements:
        alternative = replacements[ingredient]
        return alexandra.respond("That ingredient can be replaced by %s" % alternative)
    else:
        return alexandra.respond("I'm afraid I don't know of {} replacements".format(ingredient))
    # return alexandra.reprompt("We haven't met yet! What's your name?")


# for debug only
if __name__ == '__main__':
    app.run('0.0.0.0', 8088, debug=True, validate_requests=False)
