/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './debts/templates/**/*.html',  // in case we add app-level templates later
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}