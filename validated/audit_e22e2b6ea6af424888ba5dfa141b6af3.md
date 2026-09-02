### Title
Webhook shop-domain spoofing via HMAC not binding `shop-domain` header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` trusts the `shop` field taken from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header when dispatching a webhook to the app's handler, but the HMAC signature that `Utils::HmacValidator` checks only covers the raw request body, not the shop header. Any party that can obtain one validly-signed webhook body/HMAC pair for the app (e.g., by installing the app on their own store and receiving a real webhook) can replay that body+HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, and the gem will accept it as authentic and hand the attacker-chosen shop identity to the handler.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

Only `@raw_body` is signable; `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from headers and are never part of the signed material: [2](#0-1) [3](#0-2) 

`Registry.process` validates only this body-bound HMAC, then immediately trusts `request.shop` as the tenant identity passed to the app-supplied handler: [4](#0-3) 

`WebhookMetadata.shop` is the only tenant identifier surfaced to the handler: [5](#0-4) 

`HmacValidator.validate`/`validate_signature` compute the digest purely from `verifiable_query.to_signable_string` and `Context.api_secret_key` — the app's single secret shared across every shop that installs the app — with no shop-scoped component at all: [6](#0-5) 

The binding that is broken is:

`shop_identity_the_handler_acts_on == shop_that_actually_produced_and_authorized_the_signed_payload`

Because the HMAC never covers `shop`, these two values can diverge: the signature only proves "this body came from someone who knows `api_secret_key`" (true for the app's own Shopify-delivered webhooks to *any* installed shop, since the secret is per-app, not per-shop), while `shop` is attacker-controlled header data that the gem passes straight through as the trusted tenant key.

By contrast, `Auth::Oauth::AuthQuery` correctly includes `shop` inside `to_signable_string`, binding shop identity to the signature for the OAuth callback path: [7](#0-6) 

The webhook path has no equivalent binding.

### Impact Explanation
Any merchant who installs the app on a shop they control is delivered real, correctly-signed webhooks by Shopify (signed with the app's single `api_secret_key`). Because that key is shared across all shops using the app, and the HMAC never covers the shop domain, that merchant can capture a valid `(raw_body, hmac)` pair and replay it against the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop's domain. `Registry.process` will validate the HMAC successfully and invoke the app's handler with `WebhookMetadata.shop` set to the victim's domain and attacker-chosen body content, causing the app to attribute forged data/events to a shop the attacker does not control — a cross-tenant access/data-injection primitive that can drive downstream mandatory-topic handling (`shop/redact`, `customers/redact`, `customers/data_request`) or any custom handler logic keyed on `data.shop`.

### Likelihood Explanation
Requires no privileged credentials, access tokens, or `client_secret` knowledge beyond what any merchant installing the app already legitimately receives via normal webhook delivery; it only requires basic HTTP replay capability against the app's public webhook endpoint. This is reachable by an unprivileged internet user (any merchant able to install the app) and does not depend on the host application ignoring documented behavior — the gem itself performs no shop binding at the HMAC layer.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signed material used by `Request#to_signable_string`, or have `Registry.process` cross-check `request.shop` against an independently trusted source (e.g., an active session for that shop) before dispatching to the handler, so the HMAC verification and the tenant identity used downstream refer to the same, cryptographically bound value.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; Shopify delivers a legitimate webhook, e.g. `orders/create`, signed with the app's `api_secret_key`:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw body>`, body `{"id": 1, ...}`.
2. Attacker resends the identical `raw_body` and identical `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate` recomputes the HMAC over `to_signable_string` (the raw body only) and it matches, per [8](#0-7) .
4. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with `shop == "victim.myshopify.com"`, per [9](#0-8) , even though the payload was fabricated/replayed by the attacker for a different tenant.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
