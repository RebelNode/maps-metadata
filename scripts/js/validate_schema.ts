import Ajv from "npm:ajv@^8.12.0/dist/2020.js";

const schema = await Deno.readTextFile(Deno.args[0]);
const json_data = await Deno.readTextFile(Deno.args[1]);

const ajv = new Ajv({
	allErrors: true,
	useDefaults: true
});
const validate = ajv.compile(JSON.parse(schema));
const data = JSON.parse(json_data);
if (!validate(data)) {
	for (let error of validate.errors) {
		console.error(error);
	}
	throw new Error("Validation of data agains schema failed");
}

await Deno.writeTextFile(Deno.args[2], JSON.stringify(data, null, 4));
