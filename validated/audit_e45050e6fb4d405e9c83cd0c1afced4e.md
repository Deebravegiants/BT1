### Title
Webhook shop/topic identity not bound to HMAC signature allows cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` directly from unauthenticated HTTP headers, while the HMAC signature verified by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body. `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` for tenant attribution after only checking that the body's HMAC is valid, without any binding between the verified bytes and the shop the data is attributed to.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers, none of which participate in the signature: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely over `to_signable_string` (the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` gates only on this body-HMAC check, then forwards the unauthenticated `request.shop` header value straight to the app's webhook handler as the tenant identifier: [4](#0-3) 

Because the body is what's signed, not the `(shop, topic, webhook_id, api_version)` tuple, the equality the gem is supposed to guarantee — "shop the HMAC-verified bytes came from" == "shop passed to the handler" — does not hold. An attacker who legitimately installs the app on their own store receives genuine `(body, hmac)` pairs signed with the app's real `api_secret_key` for their own webhooks. They can then replay that exact body+HMAC to the app's single shared webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`/`x-shopify-webhook-id`) header with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body bytes, and `Registry.process` calls the handler with `shop: request.shop` set to the attacker-chosen victim domain, `body:` set to attacker-controlled content signed for a different (their own) shop.

### Impact Explanation
This breaks the tenant-identity binding that host applications rely on this gem to enforce ("the shop that authenticated this webhook body" vs. "the shop the app processes data for"), enabling cross-tenant data injection/confusion: an attacker-controlled webhook body can be attributed to any victim shop domain, e.g. faking `app/uninstalled` for a victim shop (causing the app to delete/deactivate a victim's real session), or injecting attacker-controlled order/product payloads into a victim shop's records. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires the attacker to install the target app on any shop they control (a normal, low-privilege action for any Shopify Partner/dev store) to obtain one valid `(body, hmac)` pair, then send a single forged HTTP POST to the app's public webhook endpoint with a substituted `shop-domain` header. No access to `api_secret_key`, access tokens, or the victim's credentials is required.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the value that's cryptographically verified, or otherwise enforce that `request.shop` matches an expected/known relationship before dispatching to the handler. Concretely:
- Include the `shop-domain` (and `topic`) header values in the signable string computed by `Request#to_signable_string`, so `HmacValidator` fails if these headers are altered from what Shopify actually signed, or
- Have `Registry.process` cross-check `request.shop` against session/subscription state (e.g. only accept webhooks for shops with an active, previously-registered subscription for that specific `webhook_id`/topic) before invoking the handler.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a legitimate webhook (e.g. `app/uninstalled`) delivered with a valid `x-shopify-hmac-sha256` computed over the JSON body using the app's real `api_secret_key`.
2. Attacker captures the raw body and the `hmac-sha256` header value from that request.
3. Attacker sends a new POST to the app's webhook endpoint with:
   - The captured raw body and `x-shopify-hmac-sha256` unchanged.
   - `x-shopify-shop-domain` replaced with `victim-shop.myshopify.com`.
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) passes because it only checks the body against the secret.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) invokes the app's handler with `shop: "victim-shop.myshopify.com"` and the attacker's body, causing the app to process attacker-controlled data as belonging to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
