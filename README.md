# IFlask-Notebook

Proof of concept for dynamically rendering IPython Notebooks using Flask.

Pages can be developed with the IPython Notebook server by entering the `notebooks` directory and running `ipython notebook`. Running `app.py` will start the Flask site which picks up all notebooks and dynamically renders only the markdown and output cells.

Next step: try rendering notebooks that use Widgets.

Ideas on better ways to do this, feedback and pull requests all welcome!
