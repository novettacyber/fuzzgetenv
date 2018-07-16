all:
	gcc --shared -fPIC -o hook.so hook.c

examples:
	make -C examples

clean:
	rm hook.so
	make -C examples clean

.PHONY: all examples clean 
