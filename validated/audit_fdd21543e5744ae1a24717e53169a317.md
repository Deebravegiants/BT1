This confirms the finding: the gem's documentation explicitly tells app developers to treat `data.shop` as an authenticated tenant identifier (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) even though that field is never covered by the HMAC signature.

### Title
Webhook `shop` field is trusted for tenant routing without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, but the `shop` value that the framework hands to the app's handler as the tenant identifier is read from an HTTP header that is never included in that HMAC computation. An attacker who can obtain any one valid `(body, hmac)` pair signed with the app's shared `client_secret` (e.g., by installing the app on their own store and receiving a real webhook) can resend that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop, and the request passes verification.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop` accessor used to build the shop-scoped payload the app receives is pulled straight from a header that is not part of the signed material: [2](#0-1) 

`Registry.process` verifies the HMAC and then hands the handler a `WebhookMetadata` object built from `request.shop`, with no cross-check that the signed body actually pertains to that shop: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (i.e. the raw body) against the app's `api_secret_key`: [4](#0-3) 

The identity binding that should hold is: `hmac_signed_content == content_the_app_acts_on`. Here, `hmac_signed_content = raw_body` while `content_the_app_acts_on = (raw_body, shop_header)`. Since `shop_header` is excluded from the signed content, the two sides of the equality diverge: a body/HMAC pair valid for Shop A can be replayed with a header claiming Shop B, and the HMAC check still passes because it never inspected the header. The gem's own documentation instructs developers to key downstream processing (e.g., job queues, per-shop DB records) directly on `data.shop`, so this un-authenticated field becomes the tenant key trusted by the host app precisely because this gem presents it as verified ("This will verify the request did indeed come from Shopify").

### Impact Explanation
Because `api_secret_key` (the app's `client_secret`) is shared across every shop that installs the app, any merchant who installs the app on a shop they control can generate arbitrary valid `(body, hmac)` pairs for topics they can trigger (e.g., `orders/create`, `products/update`, `app/uninstalled`) and then replay them against the app's public webhook endpoint with the shop header rewritten to a victim's `myshopify.com` domain. Because the gem asserts the request "did indeed come from Shopify" once the HMAC check passes, downstream app logic keyed on `data.shop` performs cross-tenant writes/actions attributed to the victim shop using attacker-controlled body content — a cross-tenant data injection into another merchant's records.

### Likelihood Explanation
Exploitation requires only: (1) the ability to install the app on any shop (a normal, unprivileged merchant action), (2) capturing one legitimate webhook delivery for a topic of interest, and (3) reissuing an HTTP POST to the app's public webhook URL with a forged `X-Shopify-Shop-Domain`/`x-shopify-shop-domain` header. No access token, secret, or privileged credential is needed beyond what any app-installing user already has.

### Recommendation
Bind the shop identity into the verified material, e.g., include the `shop-domain` (and ideally `webhook-id`/`topic`) header value in the string that is HMAC-verified, or cryptographically tie the header values to the payload before trusting `request.shop` in `Registry.process`. At minimum, document that `data.shop` is unauthenticated and that consuming apps must independently confirm the shop has an active, matching webhook/session registration before acting on the payload.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g., update a product) to receive a legitimate `(raw_body, X-Shopify-Hmac-Sha256)` pair from Shopify.
2. Replay the captured request to the app's webhook endpoint, keeping `raw_body` and `X-Shopify-Hmac-Sha256` unchanged, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` (via `Registry.process`) passes because it only checks the raw body against the shared secret: [3](#0-2) 
4. The handler executes with `WebhookMetadata#shop == "victim.myshopify.com"` even though the body content originated from the attacker's shop, causing the host app to perform actions against the victim's tenant using attacker-controlled data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
