## Title
Webhook `shop` domain used for tenant identification is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that the application uses to route and process an incoming webhook from the unauthenticated `X-Shopify-Shop-Domain` HTTP header, while the HMAC signature that `Utils::HmacValidator` verifies only covers the raw request body. Because the two are decoupled, a party who can obtain any one valid `(raw_body, hmac)` pair signed with the app's shared `client_secret` — trivially available to anyone who installs the app on their own store — can replay that pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header. The signature still validates, and `Webhooks::Registry.process` dispatches the payload to the handler tagged with the attacker-chosen `shop`, breaking the binding between the shop that produced the signed bytes and the shop the application believes sent them.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of that signable string: [2](#0-1) 

`HmacValidator.validate` only checks `hmac` against `to_signable_string` (the body), never the shop header: [3](#0-2) 

`Registry.process` trusts `request.shop` once the (body-only) HMAC passes, and forwards it as the tenant identity to the handler: [4](#0-3) 

Broken binding, stated as an equality that should hold but doesn't:
`shop_that_produced_the_signed_bytes == shop_attributed_to_the_request_by_the_app`

Since a Shopify app's webhook HMAC secret is the app's single `client_secret`, shared across every shop that has installed the app (not a per-shop secret), any unprivileged internet user can:
1. Install the target app on their own (attacker-controlled) development/test store.
2. Trigger any webhook topic the app subscribes to, capturing the legitimate `raw_body` and its `X-Shopify-Hmac-Sha256` value that Shopify sends — this pair is correctly signed with the app's real `client_secret`.
3. Replay that exact `(raw_body, hmac)` pair directly to the app's webhook endpoint, but with the `X-Shopify-Shop-Domain` header rewritten to the victim shop's domain.
4. `HmacValidator.validate` succeeds because it only re-hashes `raw_body`; the header is never part of the signed content.
5. `Registry.process` calls the app's handler with `WebhookMetadata` whose `shop` is the victim's domain, even though the payload actually originated from the attacker's own store.

### Impact Explanation
This is a cross-tenant identity confusion: the application's webhook-processing pipeline can be made to act on behalf of, or record data against, a shop the attacker does not control and never authorized. Depending on how the host app's webhook handlers use `data.shop` (e.g., looking up the merchant record to update installation state, write audit/compliance data, trigger `app/uninstalled` cleanup, or process GDPR mandatory webhooks), an attacker can inject attacker-controlled payload content that the app will associate with an arbitrary victim tenant — a cross-tenant access/integrity violation.

### Likelihood Explanation
No privileged credentials, tokens, or social engineering are required. An attacker only needs their own free/development store to install the app once and capture a legitimate webhook body+HMAC pair, then can replay it with a forged shop header indefinitely against any shop that uses the same app installation's client secret. This is directly reachable through the gem's own public API (`Webhooks::Request` / `Webhooks::Registry.process`) as documented for host app integration.

### Recommendation
Bind the `shop` value into the HMAC-signed content, or otherwise cryptographically authenticate which shop a given webhook body belongs to, before trusting the `X-Shopify-Shop-Domain` header for routing/tenant identification. At minimum, `Request#to_signable_string` (or an additional check in `HmacValidator`/`Registry.process`) should incorporate the shop domain so that a valid signature for one shop's payload cannot be replayed and reattributed to a different shop.

### Proof of Concept
```ruby
# Attacker step 1: install target app on their own dev store "attacker.myshopify.com"
# and receive a real webhook, e.g. orders/create, capturing:
raw_body = '{"id":1,"note":"hello"}'   # exact bytes Shopify sent
real_hmac = "X-Shopify-Hmac-Sha256 header value Shopify computed with the app's client_secret"

# Attacker step 2: replay to the same endpoint, victim shop header forged
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => real_hmac,      # still valid: HMAC only covers raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # attacker-controlled value
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (body-only check passes)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# The app now believes this payload came from victim-shop.myshopify.com.
``` [5](#0-4) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
