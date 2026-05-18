# adamit-club

## Publish on GitHub Pages

1. Push this repository to GitHub.
2. Open repository Settings -> Pages.
3. In Build and deployment, set Source to GitHub Actions.
4. Go to the Actions tab and wait for workflow Deploy static site to Pages to finish.

Your site URL will be:

<a href="https://chkp-igorkr.github.io/adamit-club/" target="_blank" rel="noopener noreferrer">https://chkp-igorkr.github.io/adamit-club/</a>

The root page redirects automatically to the 3D viewer in `bar/index.html`.

## If the URL still shows 404

1. Confirm the workflow run is green in Actions.
2. In Settings -> Pages, confirm Source is GitHub Actions.
3. Ensure branch main contains these files:
	- .github/workflows/pages.yml
	- index.html
	- bar/index.html
4. Wait 1 to 3 minutes and refresh the page.