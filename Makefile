output_dir = dist

cleandir:
	- cmd //C "rmdir /S /Q ${output_dir}"

build:
	make wheel
	make standalone

standalone:
	make cleandir
	pyinstaller --clean --noconfirm .build/aac.spec

wheel:
	make cleandir
	python setup.py sdist --formats=gztar  bdist_wheel

upload:
	twine upload dist/*.tar.gz dist/*.whl
