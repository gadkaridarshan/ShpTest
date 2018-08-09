// Converting editTemplateDRMEntries to Base64 representation
utf8_to_b64 = function( str ) {
  return window.btoa(unescape(encodeURIComponent( str )));
}
b64_to_utf8 = function( str ) {
  return decodeURIComponent(escape(window.atob( str )));
}

// // Returns a String compatible with the URL format (base64)
urlReadyB64 = function(str){
  return utf8_to_b64(str).replace(/\=/g, "FLAGEQUAL").replace(/\+/g, "FLAGPLUS").replace(/\//g, 'FLAGSLASH');
}
