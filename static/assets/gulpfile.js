// All rights reserved
var gulp = require('gulp');
var browserSync = require('browser-sync').create();

var plugins = require("gulp-load-plugins")({
	pattern: ['gulp-*', 'gulp.*'],
	replaceSting: /\bgulp[\-.]/
});

var reload  = browserSync.reload;

// Js
// Concat + Minifiy Js Files and move to vendor folder
var jsFiles = ['assets/js/plugins/*.js'];
var jsDest = 'assets/js/';

gulp.task('js', function () {
	return gulp.src(jsFiles)
		.pipe(plugins.order([
			'jquery.min.js',
			'bootstrap.min.js',
			'imagesloaded.pkgd.min.js',
			'*.js',
		]))
		.pipe(plugins.concat('plugins.js'))
		.pipe(gulp.dest(jsDest))
		.pipe(plugins.rename({ suffix:'.min' }))
		.pipe(plugins.uglify())
		.pipe(gulp.dest(jsDest));
});

// Css
// Concat + Minifiy Css Files and move to vendor folder
var cssFiles = 'assets/css/plugins/*.css';
var cssDest = 'assets/css/';

gulp.task('css', function () {
	return gulp.src(cssFiles)
		.pipe(plugins.order([
			'bootstrap.css',
			'*.css'
		]))
		.pipe(plugins.concat('plugins.css'))
		.pipe(gulp.dest(cssDest))
		.pipe(plugins.rename({ suffix:'.min' }))
		.pipe(plugins.cssmin({keepBreaks: true, keepSpecialComments : '*' }))
		.pipe(gulp.dest(cssDest));
});

// Sass
var sassFile = 'assets/sass/style.scss';
var sassDest = 'assets/css/';
gulp.task('sass', function () {
	return gulp.src(sassFile)
		.pipe(plugins.sass({outputStyle: 'expanded'})) // expanded - compressed - compact - nested
		.pipe(plugins.autoprefixer({
			browsers: ['last 2 versions', 'ie 9'],
			cascade: false
		}))
		.pipe(gulp.dest(sassDest));
});


// call - gulp htmlmin
// Html files minify 
// this will make your html files minified 
// make sure to copy all html files before using this
gulp.task('htmlmin', function () {
	return gulp.src('*.html')
	    .pipe(plugins.htmlmin({
	    	collapseWhitespace: true,
	    	removeComments: true,
	    	minifyJS: true, // minify js too
	    	minifyCSS: true // minify css too
	    }))
	    .pipe(gulp.dest(''))
});

// Images - Optimize jpeg and png images
gulp.task('imagemin', function () {
	return gulp.src('assets/images/**/*')
	    .pipe(plugins.imagemin())
	    .pipe(gulp.dest('assets/images'));
});


// This task will run css and js task 
// To concat all plugins folder int plugins.css or plugins.js
gulp.task('build', ['css', 'js'], function () {
	console.log('Created plugins files.');
});

// Sync - Livereload
gulp.task('browser-sync', ['sass'], function () {
	// Change virtuwell with your project's folder name
	browserSync.init({
		proxy: "localhost/virtuwell/"
	});

	// watch scss files
	gulp.watch(['assets/sass/*.scss', 'assets/sass/*/*.scss'], ['sass' , reload]);

	// watch html/php files and main.js file
	gulp.watch([
		'*.html',
		'*.php',
		'assets/js/main.js'
	]).on('change', reload);
});

// Default Task
gulp.task('default', ['browser-sync']);