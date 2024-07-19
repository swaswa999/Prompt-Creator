//BLOCKS FORM RELOADING WARNING
if ( window.history.replaceState ) {
  window.history.replaceState( null, null, window.location.href );
}

//HOMEPAGE

function aAlert(){
  alert("Success, the file was uploaded and will be in processing soon");
}

function saveDate(event){
  event.preventDefault();

  var fromValue = document.getElementById("from").value
  var toValue = document.getElementById("to").value

  document.getElementById("from").value = fromValue;
  document.getElementById("to").value = toValue;

  document.getElementById("fromHidden").value = fromValue;
  document.getElementById("toHidden").value = toValue; 

}

function refreshDate(){

  var fromValue = document.getElementById("from").value
  var toValue = document.getElementById("to").value

  document.getElementById("fromHidden").value = fromValue;
  document.getElementById("toHidden").value = toValue; 

}

// UPLOADED PAGE


