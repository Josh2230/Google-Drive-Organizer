function buildAddOn(e) {

  var card = CardService.newCardBuilder();

  var section = CardService.newCardSection()
    .addWidget(
      CardService.newTextParagraph().setText("Hello from your Drive Add-on!")
    )
    .addWidget(
      CardService.newTextButton()
        .setText('edited button')
        .setOnClickAction(
          CardService.newAction()
            .setFunctionName("onButtonClick")
        )
      );

      card.addSection(section);
      return card.build();
}

function onButtonClick(e) {
  // This will run when the button is clicked
  var card = CardService.newCardBuilder();

  var section = CardService.newCardSection()
    .addWidget(CardService.newTextParagraph().setText("You clicked the button! 🎉"))
  
  card.addSection(section);
  return card.build();

}
