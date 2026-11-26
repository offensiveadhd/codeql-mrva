/**
 * @name Naive UTC datetime calls
 * @description Every call to datetime.utcnow() or datetime.utcfromtimestamp().
 *              Both are deprecated since Python 3.12 and return a naive datetime.
 *              The demo query for the README recording: a harmless pattern, so the
 *              whole MRVA loop can be shown on real repositories.
 * @kind problem
 * @problem.severity recommendation
 * @precision high
 * @id py/demo/naive-utc-datetime
 * @tags maintainability
 */

import python
import semmle.python.ApiGraphs

from API::CallNode call, string name
where
  name = ["utcnow", "utcfromtimestamp"] and
  call = API::moduleImport("datetime").getMember("datetime").getMember(name).getACall()
select call, "datetime." + name + "() is deprecated since Python 3.12."
