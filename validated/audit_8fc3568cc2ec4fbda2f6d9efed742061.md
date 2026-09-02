## Title
Webhook shop attribution (`shop-domain` header) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the raw HTTP body against the HMAC signature, but then trusts the separate, unauthenticated `shop-domain` header to attribute the payload to a shop. Because the HMAC secret (`Context.api_secret_key`, the app's client secret) is shared across every shop that has installed the app, any merchant who installs the app can capture a genuinely-signed webhook body/HMAC pair and replay it with a different `shop-domain` header, causing the handler to process the payload as if it originated from an arbitrary victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers, none of which participate in the signature: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate`, then immediately forwards `request.shop` (the unauthenticated header) to the handler as the trusted tenant identifier: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only ever checks `verifiable_query.to_signable_string` (the body) against `Context.api_secret_key`: [4](#0-3) 

`Context.api_secret_key` is the app's single client secret, identical for every shop that has the app installed — it is not shop-specific. Consequently the equality the code implicitly relies on, `hmac_valid(body, api_secret_key) == body_originated_from(shop_header)`, does not hold: HMAC validity only proves "some shop that has this app installed sent this body", not "this specific `shop_header` value sent this body". This is exactly the class of bug described in the analog report — a value acted upon (`shop`) that is not covered by the HMAC that is supposed to authenticate the whole request.

### Impact Explanation
Any user who can freely install the target app on their own (e.g. free development) store becomes able to:
1. Trigger any webhook topic on their own shop and capture the resulting `raw_body` + valid `shopify-hmac-sha256` header (this is completely legitimate traffic they are entitled to receive).
2. Replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with a victim shop's domain.
3. `Registry.process` will accept the request (HMAC check passes because it only checks the body) and hand the handler a `WebhookMetadata` object whose `shop` is the attacker-chosen victim domain.

Any host application logic keyed off `shop` (e.g. `app/uninstalled` clearing/marking sessions, GDPR `shop/redact`/`customers/redact` deleting data, billing/plan updates, inventory or order sync writing into the wrong tenant's records) can be forced to act against a shop the attacker does not control. This is cross-tenant action/data corruption performed against a tenant the attacker has no relationship with, satisfying the Critical "cross-tenant access" bar.

### Likelihood Explanation
The prerequisite (installing the app on an attacker-controlled shop to obtain one legitimate webhook body/HMAC pair) is trivial for any unprivileged internet user — no leaked credentials, no access token, and no interaction with the victim are required. The victim shop domain just needs to be known or guessed (myshopify.com subdomains are frequently public/guessable).

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the value that is actually verified, rather than trusting a separate header:
- Include the `shop-domain` (and other headers used for routing/attribution) inside `to_signable_string`, or
- Verify a per-shop secret/HMAC where feasible, or
- At minimum, document prominently that `Webhooks::Request#shop` is not authenticated by the HMAC and must not be used as the sole tenant identifier by host applications — instead the host must cross-check it against a shop it already has an active session/install record for.

### Proof of Concept
```ruby
# Attacker installs the target app on their own dev store "attacker.myshopify.com"
# and triggers any webhook (e.g. "orders/create"). Shopify sends:
#   body:    '{"id": 1, "note": "hello"}'
#   headers: {
#     "X-Shopify-Topic" => "orders/create",
#     "X-Shopify-Hmac-Sha256" => "<valid HMAC of body using the app's shared client secret>",
#     "X-Shopify-Shop-Domain" => "attacker.myshopify.com"
#   }

captured_body = '{"id": 1, "note": "hello"}'
captured_hmac = "<valid HMAC captured above>"

# Attacker replays the SAME body + HMAC, but swaps the shop header to a victim:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled value
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) passes because it only checks `captured_body` against
# the app's shared client secret — it never checks that the secret/body pair actually
# belongs to "victim-shop.myshopify.com".
# The handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", ...) and acts
# on behalf of a shop the attacker does not control.
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
