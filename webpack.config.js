// Import the 'path' module at the top of the file
// Import the 'path' module at the top of the file
const path = require('path');

module.exports = {
  entry: './js/main.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js'
  },
 module: {
   rules: [{
     test: /\.js$/,
     exclude: /node_modules/,
     use: {
       loader: 'babel-loader',
       options: {
         presets: ['react']
       }
     }
   }]
 }
}
