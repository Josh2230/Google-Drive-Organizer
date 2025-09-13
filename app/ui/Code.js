function buildAddOn(e) {
  /*
  Creates the entry point for rendering a google workspace add-on card
  card is the empty scaffold and you add sections to it
  */

  var card = CardService.newCardBuilder();

  // This section creates the organize folder by date button
  var section = CardService.newCardSection()
    .addWidget(
      CardService.newTextParagraph().setText("Hello from your Drive Add-on!")
    )
    .addWidget(
      CardService.newTextButton()
        .setText('Create Folders By Date')
        .setOnClickAction(
          CardService.newAction()
            .setFunctionName("callFastAPI")
        )
  );

  // This section will create the undo button 
  var section2 = CardService.newCardSection()
    .addWidget(
      CardService.newTextButton()
        .setText('Undo')
        .setOnClickAction(
          CardService.newAction()
            .setFunctionName("onButtonClick")
        )
    );

      // add sections to the main card
      card.addSection(section);
      card.addSection(section2);

      // build convertes the card builder object into a real card that google can render
      return card.build();
}

/*
Will contain the functionality to undo what the user just did
*/
function onButtonClick(e) {
  // This will run when the button is clicked
  var card = CardService.newCardBuilder();

  var section = CardService.newCardSection()
    .addWidget(CardService.newTextParagraph().setText("date function here"))
  
  card.addSection(section);
  return card.build();

}

/*
callFastAPI calls the list-files endpoint (to be changed) so we can
create link the backend to the button at the frontend
*/
function callFastAPI() {

  // save the ngrok url
  var url = "https://05e05e49a783.ngrok-free.app/list-files";

  // set options for the type of request and a header to bypass warning
  var options = {
    method: "GET",
    headers: {
      "ngrok-skip-browser-warning": "1"  
    }
  };

  // fetch the response by sending the request to ngrok url
  var response = UrlFetchApp.fetch(url, options);

  //parse the JSON string from API to a javascript object
  // we usually parse json for readability because json is ugly
  var data = JSON.parse(response.getContentText());
  var files = data.files;
  
  // convert javascript object to string for card format
  // var message = data.message || JSON.stringify(data);

  var message = files.map(data => `${data.name}, ${data.createdTime}`).join("\n");
  // var message = files.map(data => `${data.id}`).join("\n"); 

  // create a new card because cards are immutable once rendered so we can't update content
  // inside an existing card directly
  // To show new data, we must replace the old card with a new card object
  var card = CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle("API Response"))
    .addSection(
      CardService.newCardSection()
        .addWidget(CardService.newTextParagraph().setText(message))
    )
    .build();

    // newActionResponseBuilder is responding to some user action
    // setNavigation tells google what to do with the sidebar view
    // updateCard(card) replaces the current card with this new one
    return CardService.newActionResponseBuilder()
      .setNavigation(CardService.newNavigation().updateCard(card))
      .build();
}
