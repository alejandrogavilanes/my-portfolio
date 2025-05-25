// Import the 'path' module
const path = require('path');

// Rest of the code...


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
