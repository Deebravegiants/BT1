### Title
Webhook shop-domain identity spoofing due to HMAC not covering the `shop`, `topic`, `webhook-id`, and `api-version` headers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `api-version`, and `webhook-id` values used to act on the webhook are read from unauthenticated HTTP headers. Because HMAC validation for webhooks uses the app-level `api_secret_key` (shared across every shop that installs the app) rather than anything shop-specific, any user who legitimately installs the app on their own store can capture one valid `(body, hmac)` pair from their own webhook traffic and replay it against the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header naming a different, victim shop. The library will accept it as authentic and dispatch it to the app's handler as if it originated from the victim shop.

### Finding Description
`Request#to_signable_string` only returns the raw body: [1](#0-0) 

and `shop`, `topic`, `api_version`, `webhook_id` are pulled straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` verifies only `verifiable_query.to_signable_string` (i.e. the raw body) against `Context.api_secret_key`: [3](#0-2) 

`Webhooks::Registry.process` trusts `request.shop` (and the other unauthenticated headers) once the HMAC check on the body passes, and forwards them straight to the app's handler: [4](#0-3) 

The identity binding that should hold is `verified_source_shop == shop_acted_on_by_handler`. In reality:
- The left side doesn't exist: the HMAC only proves "this body was signed with this app's shared secret," which is identical for every shop that has installed the app — it carries no shop-specific information.
- The right side (`request.shop`) is taken from a plain, attacker-editable HTTP header.

Since `api_secret_key` is shared across all merchants of the app (not per-shop), any of the app's own merchants can capture a `(raw_body, X-Shopify-Hmac-Sha256)` pair from a real webhook delivered to their own shop, then POST that same body/HMAC to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `topic`/`webhook-id`, which are also unauthenticated). `HmacValidator.validate` will return `true` because the body's HMAC is unchanged and still verifies against the shared secret, and `Registry.process` will hand the forged `shop`/`topic` to the handler as if the event genuinely originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: a party with no access to the victim shop can make the host application believe it received a webhook (of an attacker-chosen topic, using attacker-crafted body content up to needing a matching signature) attributed to the victim shop. Depending on how the host app's webhook handlers key off `WebhookMetadata#shop` (e.g. looking up and mutating stored per-shop state, canceling subscriptions, or triggering data deletion/GDPR flows), this enables cross-tenant data corruption or spoofed actions against a shop the attacker does not control — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is high: exploitation requires no possession of `api_secret_key`, access tokens, or the victim's credentials — only that the attacker is (or was) a legitimate merchant of the same app, which lets them harvest one valid `(body, hmac)` pair from their own store's webhook traffic and replay it with a different `Shop-Domain` header value to the shared webhook endpoint.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the value that is HMAC-verified, or otherwise cryptographically bind them — e.g., derive/verify the `shop` from a per-shop session/credential lookup rather than trusting the raw header, and/or require the app to cross-check `request.shop` against an existing installed-shop record before dispatching. At minimum, document prominently that `Request#shop`/`#topic`/`#webhook_id` are NOT covered by the HMAC and must not be trusted for authorization decisions without additional verification (e.g., confirming the shop has an active session/install record).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and subscribes/receives any real webhook, capturing the raw request body `B` and its `X-Shopify-Hmac-Sha256: H` header (a legitimate signature computed with the shared `api_secret_key`).
2. Attacker sends a new POST to the app's webhook endpoint with:
   - Body: `B` (unchanged, so the HMAC stays valid)
   - `X-Shopify-Hmac-Sha256: H`
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic`/`X-Shopify-Webhook-Id`: optionally changed
3. The app constructs `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` and calls `ShopifyAPI::Webhooks::Registry.process(request)`.
4. `Utils::HmacValidator.validate(request)` returns `true` because it only checks `B` against `Context.api_secret_key`, per: [5](#0-4) 
5. `Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"`, `topic`, and `body` all attacker-controlled, per: [6](#0-5) , causing the host application to act as though the event genuinely came from the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
