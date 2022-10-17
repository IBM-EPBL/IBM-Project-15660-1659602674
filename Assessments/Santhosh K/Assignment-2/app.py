from website import create_app

webapp = create_app()
if __name__ == "__main__":
    webapp.run(debug=True)
    # pass
