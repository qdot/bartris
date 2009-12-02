	-- Super Mario Bros. script by 4matsy.
	-- 2008, September 11th.
	--Displays the # of lives for Mario and a HP meter for Bowswer

	require("shapedefs");
	require("osc.client");

	local flag_msg = {'/mario/flag', 'i', 0}
	local coin_msg = {'/mario/coin', 'i', 0}
	local sky_msg = {'/mario/sky', 'i', 2}
	local speed_msg = {'/mario/speed', 'i', 0}
	local enemy_msg = {'/mario/enemy', 'i', 0}
	local enemy_off_msg = {'/mario/enemy', 'i', 0}
	local die_msg = {'/mario/die', 'i', 0}
	local oscclient = osc.client.new{host = '10.211.55.2', port = 9001} --57120}

	local SKY_BYTE = 0x0742
	local COIN_BYTE = 0x075e
	local SPEED_BYTE = 0x0057
	local LIVES_BYTE = 0x75a
	local ENEMY_STATE_BEGIN = 0x001e
	local ENEMY_STATE_END = 0x0022

	local last_sky = memory.readbyte(SKY_BYTE)
	local is_flagged = 0
	local last_coin = memory.readbyte(COIN_BYTE)
	local last_speed = memory.readbyte(SPEED_BYTE)
	local enemy_state = {0,0,0,0,0,0}
	local last_lives = memory.readbyte(LIVES_BYTE)

	function hasbit(x, p)
		return x % (p + p) >= p
	end;

	function text(x,y,str)
		if (x > 0 and x < 255 and y > 0 and y < 240) then
			gui.text(x,y,str);
		end;
	end;

	while (true) do

		-- print player's lives...I always thought this was a major omission of the status bar :p
		text(63,13,"x"..memory.readbyte(LIVES_BYTE)+1);

		-- If 0x0717 is > 0, we're in demo mode. Ignore.
		-- however, there's apparently no continue in lua, so we
		-- can't early exit. WTF.
		if (memory.readbyte(0x0717) == 0) then
			-- Message for coin - Pour coke
			if (last_coin ~= memory.readbyte(COIN_BYTE)) then
				coin_msg[3] = memory.readbyte(COIN_BYTE)
				last_coin = memory.readbyte(COIN_BYTE)
				oscclient:send(coin_msg);
			end;
			-- Message for flag begin. Pour rum, vibrate
			if (memory.readbyte(0x070f) > 0 and is_flagged == 0) then
				flag_msg[3] = memory.readbyte(0x070f)
				is_flagged = 1;
				oscclient:send(flag_msg);
			end;
			-- Reset flag state
			if (memory.readbyte(0x070f) == 0 and is_flagged == 1) then
				is_flagged = 0;
			end;
			-- Message for speed/wind for ambx
			if (memory.readbyte(SPEED_BYTE) ~= last_speed) then
				speed_msg[3] = memory.readbyte(SPEED_BYTE);
				last_speed = memory.readbyte(SPEED_BYTE);
				oscclient:send(speed_msg);
			end;

			if (memory.readbyte(SKY_BYTE) ~= last_sky) then
				sky_msg[3] = memory.readbyte(SKY_BYTE);
				last_sky = memory.readbyte(SKY_BYTE);
				oscclient:send(sky_msg);
			end;

			if (memory.readbyte(LIVES_BYTE) <  last_lives) then
				die_msg[3] = memory.readbyte(LIVES_BYTE);
				last_lives = memory.readbyte(LIVES_BYTE);
				oscclient:send(die_msg);
			end;

			-- Enemy state detection anpd rum pouring
			for v = ENEMY_STATE_BEGIN, ENEMY_STATE_END, 0x1 do
				if(hasbit(memory.readbyte(v), 3)) then
					if (enemy_state[v - (0x1d)] == 0) then
						oscclient:send(enemy_msg);
						sky_msg[3] = 3;
						--oscclient:send(sky_msg);
						enemy_state[v - (0x1d)] = 1;
					end;
				else
					--if (enemy_state[v - (0x1d)] == 1) then
					--	last_sky = 0xff;
					--end;

					enemy_state[v - (0x1d)] = 0;
				end;
			end;

		end;

		FCEU.frameadvance();
	end;
