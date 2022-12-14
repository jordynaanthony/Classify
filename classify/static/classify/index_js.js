function openDpt(dptName, elmnt) {
    // Hide all elements with class="tabcontent" by default */
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
  
    // Remove the background color of all tablinks/buttons
    tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].style.backgroundColor = "";
      tablinks[i].id="";
    }
  
    // Show the specific tab content
    document.getElementById(dptName).style.display = "block";
  
    // Make on-using department yellow to emphasis
    elmnt.style.backgroundColor = "#777";
    // make on-using department the default one when coming back to index page
    //elmnt.id = "defaultOpen_dpt";

    // Give each button(subjects) an id
    var subject;
    subject = document.getElementsByName(dptName);
    for (i = 0; i < subject.length; i++) {
      subject[i].id=dptName+i;
    }
  }

function choose_subject(elmnt,dptName) {
    var subject;
    subject = document.getElementsByName(dptName);
    for (i = 0; i < subject.length; i++) {
        subject[i].style.backgroundColor = "";
    }
    elmnt.style.backgroundColor = "#777";
}

// function set_defaultdpt(){
//   var defaultdpt;
//   defaultdpt = document.getElementById("current_subject");
//   alert(defaultdpt.value);
// }

function find_search_subject(form) {
    //var myVar = "Engr";
    //window.location.href = window.location.href.replace(/[\?#].*|$/, "?param=" + myVar); //Send the variable to the server side
    // set compare color to grey
    var colorToCompare = "rgb(119, 119, 119)";
    // we first choose the onsubmitting department
    var dpt_list;
    dpt_list = document.getElementsByClassName("tablink");
    var current_dpt;
    for (i = 0; i < dpt_list.length; i++){
      if(dpt_list[i].style.backgroundColor===colorToCompare){
        current_dpt=dpt_list[i];
        break;
      }
    }

    // then search specific subject in that department
    var subject;
    var subject_id;
    subject = document.getElementsByClassName("subject_search");
    // index of the list for arts and science department with "African-American & African Studies" to be 0 and "Mathematics" to be 1
    // Arts_Science = [["African-American & African Studies", "Mathematics"], ["American Studies", "Media Studies"],["Anthropology", "Middle Eastern & South Asian Languages & Cultures"],
    // ["Art","Music"],["Astronomy","Philosophy"],["Biology","Physics"],["Chemistry","Politics"],["Classics","Public Health Sciences"],["Drama","Psychology"],
    // ["East Asian Languages, Literatures & Cultures","Religious Studies"],["Economics","Slavic Languages & Literatures"],["English","Sociology"],
    // ["Environmental Sciences","Spanish, Italian & Portuguese"],["French Language & Literature","Statistics"],["German Languages & Literatures","Women, Gender, and Sexuality"],["History",""]]
    
    for (i = 0; i < subject.length; i++) {
      if(subject[i].name==current_dpt.value){
        if(subject[i].style.backgroundColor===colorToCompare){
          subject_id=subject[i].id;
          if(subject_id=="A&S_dpt1"){
            form.action="Mathematics_fall2022";
            return true;
          }
          if(subject_id=="A&S_dpt4"){
            form.action="ANTH_fall2022";
            return true;
          }
          if(subject_id=="Engr8"){
            form.action="Computer_Science_fall2022";
            return true;
          }
        }
      }
    }
    //alert("please choose a subject")
    return false;
}