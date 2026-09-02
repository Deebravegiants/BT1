### Title
Webhook `shop`, `topic`, and `webhook_id` fields are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body (`to_signable_string` returns `@raw_body`), while the `shop`, `topic`, `api_version`, and `webhook_id` values are read directly from unauthenticated HTTP headers. `Webhooks::Registry.process` verifies the HMAC and then unconditionally trusts `request.shop` (and `request.topic`) as the tenant identity when dispatching to the app's handler. Any party who can obtain one genuinely-signed webhook body (e.g., by installing the app on their own store) can replay that exact body with a forged `shop-domain` header pointing at a victim shop, and the gem will report it as HMAC-valid and hand the handler data purporting to be from the victim shop.

### Finding Description
The HMAC binding equality that should hold is:
`HMAC(api_secret_key, bytes_verified) == HMAC(api_secret_key, bytes_the_app_acts_on_for(shop, topic, webhook_id))`

In this gem that equality is broken:

- `to_signable_string` only returns `@raw_body`: [1](#0-0) 
- `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers with no cryptographic binding to the signed body: [2](#0-1) 
- `HmacValidator.validate` only ever hashes `verifiable_query.to_signable_string`, i.e. the raw body, so header tampering never affects the check: [3](#0-2) 
- `Registry.process` validates the HMAC and then immediately forwards `request.shop` and `request.topic` to the app's handler as trusted tenant/topic identity, with no separate verification: [4](#0-3) 

Because `shop` (the tenant identity acted upon by the handler) is not part of the bytes verified by the HMAC (only the body is), an attacker who owns any Shopify store (a normal, unprivileged action requiring no leaked secret or access token) can:
1. Install the target app on their own store and capture one legitimately Shopify-signed webhook POST (raw body + `X-Shopify-Hmac-Sha256` header) for a topic the app subscribes to.
2. Replay that exact body and HMAC header to the app's webhook endpoint, but swap `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) to name a victim shop.
3. `Utils::HmacValidator.validate(request)` still succeeds, because it only hashes `@raw_body`, which was untouched.
4. `Registry.process` invokes the handler with `shop: <victim-shop>` and attacker-controlled `body`, causing the app to treat attacker-supplied content as authentic data belonging to the victim tenant.

### Impact Explanation
This breaks the tenant identity binding the HMAC is supposed to enforce, allowing an unprivileged internet user (anyone with a Shopify dev/store account, no app credentials required) to inject data attributed to an arbitrary other shop into any app built on this gem's webhook handling — a cross-tenant access/confusion vulnerability, matching the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high: obtaining one genuine signed webhook body only requires installing the target app on an attacker-owned store (a normal onboarding flow, not a privileged action), and no part of the app's `client_secret` or any merchant access token is needed to forge the `shop`/`topic` attribution afterward — only header rewriting on a replayed HTTP request.

### Recommendation
Bind the shop (and topic/webhook id) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived `shop` to the signed body (e.g., require the app to independently confirm the shop via a signed webhook payload field, or reject requests whose header-derived shop cannot be verified against the request source). At minimum, document prominently that `Request#shop`/`#topic`/`#webhook_id` are unauthenticated and must not be used as a tenant boundary unless additionally corroborated.

### Proof of Concept
1. Register a handler with `ShopifyAPI::Webhooks::Registry.add_registration(topic: "orders/create", ...)`.
2. As attacker, install the app on `attacker-shop.myshopify.com`, trigger an `orders/create` webhook, and capture the raw POST body `B` and header `X-Shopify-Hmac-Sha256: H` (a valid HMAC of `B` under the app's `api_secret_key`, which the attacker never sees but Shopify computed for them).
3. Replay to the app's webhook endpoint:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: H
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   <body B>
   ```
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` and `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` and matches `H` — validation passes.
5. The handler receives `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, so the app processes attacker-controlled order data as if it belongs to `victim-shop.myshopify.com`.

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
