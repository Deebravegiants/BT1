## Finding

### Title
Webhook shop, topic, and webhook-id headers are not covered by the HMAC signature, enabling cross-tenant webhook forgery via replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The webhook signature verification in this gem authenticates only the raw request body, never the `shop-domain`, `topic`, or `webhook-id` headers. Any holder of one genuinely-signed `(body, hmac)` pair — such as an attacker who installs the app on their own store and receives their own legitimate webhook — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary victim `shop-domain` (and/or `topic`/`webhook-id`) header. `Utils::HmacValidator` still reports the signature valid, and `Webhooks::Registry.process` dispatches the attacker-supplied body to the handler tagged with the attacker-chosen shop, breaking the binding between "the shop the HMAC actually vouches for" and "the shop the handler is told the data belongs to."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The identifying metadata (`shop`, `topic`, `webhook_id`, `api_version`) is read straight from unauthenticated HTTP headers with no cryptographic binding to the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC only over `to_signable_string` (i.e., the body) and compares it against the `hmac` header — it never incorporates `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Webhooks::Registry.process` then trusts these unauthenticated fields directly to select the handler and to construct the `WebhookMetadata` passed to application code, using `request.shop` as the tenant identity: [4](#0-3) 

Because the same `api_secret_key` is shared across every shop that installs the app, a low-privilege attacker who merely installs the app on their own store can capture one legitimately Shopify-signed `(body, hmac)` pair from a webhook addressed to their own shop. Since the signature covers only the body, that exact `(body, hmac)` pair remains valid no matter what `shop-domain` (or `topic`/`webhook-id`) header is sent with it. The broken identity equality is:

`shop authenticated by HMAC (∅, since HMAC covers only body) ≠ shop trusted by Registry.process (request.shop header)`

### Impact Explanation
This lets an attacker who controls no more than their own installed-app store forge webhook deliveries that the host application will process as belonging to a different, victim shop — i.e., cross-tenant data injection into whatever the host app's webhook handlers do (e.g., creating records, updating billing/plan state, revoking data, or triggering GDPR-style deletion flows keyed off `shop`). This is a cross-tenant access primitive delivered entirely through this gem's own webhook verification/dispatch logic, without any access token, `client_secret`, or victim credential.

### Likelihood Explanation
Exploitability only requires: (1) installing the app on an attacker-controlled shop (a normal, unprivileged action available to anyone who can create a Shopify dev/trial store), (2) capturing one legitimately delivered webhook to that shop, and (3) replaying it with a modified `shop-domain`/`topic` header to the app's public webhook endpoint. No secret material or elevated privilege is required — the entire header set the app relies on for tenant attribution is unauthenticated by design in this code path.

### Recommendation
Bind the identifying headers into the signed material (or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the HMAC verification), or require the host application to cross-check `request.shop` against an independently known, previously-provisioned shop record before dispatching. At minimum, document/deprecate reliance on `request.shop`/`request.topic` as trusted identifiers unless additional server-side shop validation (e.g., confirming the shop has an active session/install record) is performed before invoking handlers.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header value `H` that Shopify sent — `H` is a valid HMAC-SHA256 of `B` under the app's shared `api_secret_key`.
2. Attacker sends a new POST request to the app's webhook endpoint with the same body `B` and header `H`, but sets:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: orders/create` (or another registered topic)
3. `ShopifyAPI::Webhooks::Request.new` builds successfully (all required headers present), and `Utils::HmacValidator.validate` returns `true` because it only recomputes HMAC over `B`, matching `H` — see [5](#0-4) .
4. `Webhooks::Registry.process` dispatches to the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: JSON.parse(B), ...)`, as shown in [6](#0-5) , causing the host app to process attacker-controlled data attributed to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-21)
```ruby
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
