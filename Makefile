export ROOT_PATH = ../../i2c_ip_env/
export OUT_ROOT_PATH = ./output/
export DECRYPT_ROOT_PATH = ./decrypt/

readme:
	@echo "           1.ROOT_PATH could be a proj root-path"
	@echo "           2.set OUT_ROOT_PATH as a back-up proj root-path"
	@echo "           3.use [make clean copy run] create a back-up proj with .v & .sv encrypted"
	@echo "           4.skip_file_name.lst contains .v & .sv files dont want to be encrypted like std-cell"
	@echo "           5.if ROOT_PATH include sim-proj , be careful with sim .v .sv reg & wire vars"
	@echo "           6.Recovery encrypted RTL func is not supported right now"

clean:
	rm -rf $(OUT_ROOT_PATH)
copy:
	cp $(ROOT_PATH) $(OUT_ROOT_PATH) -rf
run:
	python3 rtl_encryption.py | tee run.log
