from flask import Flask, current_app, url_for, redirect


def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(config)

    app.debug = debug
    app.testing = testing

    # Register landing API blueprint
    from bot.bot import igetmad
    app.register_blueprint(igetmad, url_prefix='/bot')

    from landing.landing import landing
    app.register_blueprint(landing, url_prefix='/welcome')

    # Add a default route as landing page
    @app.route('/')
    def salam():
        return redirect(url_for('landing.welcome'))

    # Add an error handler. This is useful for debugging the live application,
    # however, you should disable the output of the exception for production
    # applications.
    @app.errorhandler(500)
    def server_error(e):
        return """
        An internal error occurred: <pre>{}</pre>
        See logs for full stacktrace.
        """.format(e), 500

    return app
