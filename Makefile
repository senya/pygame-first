tags:
	rm tags
	find . -name '*.py' -print | xargs ctags -a
.PHONY: tags

cscope:
	find . -name '*.py' ! -type l -print > cscope.files
	cscope -bkqu
.PHONY: cscope
