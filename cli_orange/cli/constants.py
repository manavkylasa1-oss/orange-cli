MAIN_MENU = 0
MANAGE_USERS = 1
MANAGE_PORTFOLIOS = 2
MARKETPLACE = 3
EXIT = -1
LOGIN_MENU = -2   

MENUS = {
      LOGIN_MENU: """[bold]Welcome to orange , a CLI based investment app[/bold]
1. Admin login
2. User login
3. New user sign-up
0. Exit""",
    MAIN_MENU: """[bold]Main Menu[/bold]pyth
1. Manage application users
2. Manage portfolios
3. Visit marketplace
0. Exit""",
    MANAGE_USERS: """[bold]Manage Users (admin only)[/bold]
1. View users
2. Create new user
3. Delete user
9. Back""",
    MANAGE_PORTFOLIOS: """[bold]Manage Portfolios[/bold]
1. View my portfolios
2. Create new portfolio
3. Delete a portfolio
4. Sell securities (liquidate)
9. Back""",
    MARKETPLACE: """[bold]Marketplace[/bold]
1. View securities
2. Place purchase order
9. Back"""
}
