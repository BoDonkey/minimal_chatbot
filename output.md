Creating an article piece in ApostropheCMS and displaying it on your site involves several steps, including defining the piece type, creating a piece page type to display the articles, and optionally creating widgets to display articles in various places on your site. Here's a step-by-step guide to accomplish this: ### 1. Create the Article Piece Type First, you need to define the article piece type. This involves creating a new module for articles.
1. **Create the Module** In your project's `modules` folder, create a folder named `article`. Inside this folder, create an `index.js` file.
2.  **Define the Article Piece Type** Edit the `modules/article/index.js` file to define the fields for your articles.

```javascript
module.exports = { extend: '@apostrophecms/piece-type', options: { label: 'Article', pluralLabel: 'Articles' }, fields: { add: { title: { type: 'string', label: 'Title', required: true }, body: { type: 'area', label: 'Body', options: { widgets: { '@apostrophecms/rich-text': { toolbar: [ 'bold', 'italic', 'link' ] }, '@apostrophecms/image': {} } } } }, group: { basics: { label: 'Basics', fields: ['title', 'body'] } } } };
```

3. **Register the Article Module** In your project's `app.js`, add the article module to the modules section.

```javascript
require('apostrophe')({ shortName: 'my-project', modules: { article: {}, // other modules... } });
```
### 2. Create the Article Page Type To display articles, you'll need a page where they can be listed and individual articles can be viewed.

1. **Generate the Article Page Module** Use the CLI to generate the article page module with the `--page` option.
```bash
apos add piece article --page 
```
This will create a `article-page` module with `index.html` and `show.html` templates.

2. **Configure the Article Page Module** Edit the `modules/article-page/index.js` to specify it should display articles.

```javascript 
module.exports = { extend: '@apostrophecms/piece-page-type', options: { label: 'Article Page', pluralLabel: 'Article Pages', pieceModuleName: 'article' } };
```
3. **Add the Article Page Type to the Page Module** In `modules/@apostrophecms/page/index.js`, add the article page type to the `types` array.

```javascript
module.exports = { options: { types: [ { name: '@apostrophecms/home-page', label: 'Home' }, { name: 'article-page', label: 'Article Page' } // other page types... ] } };
```
### 3. Display Articles on the Site - 
- **List Articles**: Use the `index.html` template in the `article-page` module to list articles. You can loop through `data.pieces` to display each article's title and a link to its full content.
- **Show Individual Articles**: The `show.html` template in the `article-page` module is used to display individual articles. Access the article content using `data.piece`.

### 4. (Optional) Create Widgets to Display Articles You can also create widgets to display articles in different areas of your site, such as the homepage or sidebar. 
This involves creating a new widget module, defining the widget's schema to include a relationship field to the article piece, and then adding the widget to areas in your templates. By following these steps, you'll have a fully functional system for managing and displaying articles on your ApostropheCMS-powered site.