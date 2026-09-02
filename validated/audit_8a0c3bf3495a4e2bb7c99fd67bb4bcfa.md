### Title
Webhook shop/topic/webhook-id identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the request body, then dispatches to the app's handler using the `shop`, `topic`, and `webhook_id` values taken directly from HTTP headers, which are never covered by that signature: [1](#0-0) 

The HMAC verification only signs the raw body, per `VerifiableQuery#to_signable_string`: [2](#0-1) 

`HmacValidator.validate` computes the signature strictly from `verifiable_query.to_signable_string` (the raw body for webhooks) and the app's `api_secret_key`: [3](#0-2) 

The `shop`, `topic`, `webhook-id`, and `api-version` values are read from headers, entirely outside the signed bytes: [4](#0-3) 

The identity binding this breaks is: `hmac_valid(raw_body, api_secret_key) == true` is treated as proof that `(shop, topic, webhook_id)` are authentic, when in fact those fields are only "bytes parsed" from unauthenticated headers, never "bytes verified" by the HMAC. Since `api_secret_key` is shared by the app across *every* shop that installs it, any unprivileged user who installs the app on their own (e.g. free/dev) store can legitimately receive one valid `(raw_body, hmac)` pair for a topic they control (e.g. `app/uninstalled`, `orders/create` on their own store), then replay that exact body+signature to the same webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) header with a victim shop's domain. `Registry.process` will validate the (unchanged, genuinely-signed) body and hand the handler a `WebhookMetadata` claiming to be from the victim shop: [5](#0-4) 

Any handler that uses `data.shop` to look up a stored session/access token and act on behalf of "the shop that sent this webhook" (the documented and expected usage pattern, e.g. mandatory `customers/redact`/`shop/redact` handling or order processing) will now perform that action against the victim tenant using data the attacker fully controls, purely because the shop identity field is unauthenticated.

### Impact Explanation
This breaks the tenant-identity boundary the webhook subsystem is supposed to enforce: an attacker with no privileges beyond owning any shop that installs the app can force the app to process attacker-supplied webhook payloads under another merchant's identity. Depending on the app's handler logic (which trusts `WebhookMetadata#shop` as authenticated, as the library's own webhook docs instruct), this enables cross-tenant data manipulation/impersonation — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app that registers webhooks and relies on the `shop` field from `WebhookMetadata` to select which tenant's data/session to touch — this is the only way `Registry.process` communicates shop identity to the handler, and the library performs no cross-check between the signed body and the header-derived shop/topic/webhook_id. No credentials, access tokens, or `api_secret_key` are needed by the attacker; only the ability to install the app on a shop they control (which any internet user can do) and to send a raw HTTP POST with edited headers to the app's public webhook endpoint.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the signed material, or otherwise cryptographically tie them to the request that Shopify actually sent:
- Include `shop`, `topic`, and `webhook_id` in the HMAC-signable string (this requires a corresponding change to how Shopify signs outgoing webhooks, so at minimum the library should document/enforce that callers must independently verify `data.shop` against a shop they already have an active, previously-established session for, rather than treating it as trusted purely because `HmacValidator.validate` returned `true`).
- At minimum, raise/require verification that `request.shop` corresponds to a shop for which the app currently holds a stored session before any stateful action is taken based on that shop value, and make this an explicit, mandatory step in `Registry.process` rather than leaving it to individual app implementations.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, obtaining legitimate webhook deliveries such as `orders/create` with a valid `X-Shopify-Hmac-Sha256` computed over the JSON body using the app's shared `api_secret_key`.
2. Attacker captures one such `(raw_body, hmac)` pair.
3. Attacker POSTs the exact same `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (a shop they do not control).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `raw_body` against the HMAC — it succeeds because the body/signature pair is genuinely valid: [6](#0-5) 
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and `body:`/`topic:` fully attacker-controlled, and performs whatever action the app implements for that topic against the victim tenant's stored session.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

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
