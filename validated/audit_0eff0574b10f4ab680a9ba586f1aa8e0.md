### Title
Webhook shop/topic/id attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the request body against the `X-Shopify-Hmac-SHA256` header, then unconditionally trusts the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers to build the `WebhookMetadata` handed to the app's handler. None of those identity fields are covered by the signature.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Registry.process` validates that signable string with `Utils::HmacValidator.validate(request)`, and then immediately builds a `WebhookMetadata` object using `request.shop`, `request.topic`, and `request.webhook_id`, all of which are read straight from unauthenticated headers: [2](#0-1) [3](#0-2) 

The HMAC secret used to validate the body (`Context.api_secret_key`, the app's `client_secret`) is the same for every shop that has installed the app — Shopify signs each merchant's webhook body with the app's shared secret, not a per-shop key: [4](#0-3) 

The binding that should hold is: `shop header == shop that the signed bytes originated from`. Before the request: an attacker who is a legitimate (even trial/free) installer of the app receives their own webhooks with a body and a valid HMAC computed over that body using the app's shared secret. After the request: the attacker replays that exact body/HMAC pair to the app's webhook endpoint but substitutes the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header with a victim shop's domain or an ID belonging to another tenant's resource. `Utils::HmacValidator.validate` still succeeds because it only checks the body bytes, and `Registry.process` forwards the attacker-chosen `shop` value straight to the handler as if it were authenticated. This breaks the equality "bytes verified == identity attributed to those bytes," letting the attacker's own signed payload be attributed to a different merchant.

### Impact Explanation
If the host application's webhook handler uses `WebhookMetadata#shop` (or `webhook_id`) to select which tenant's data to mutate — the intended and documented usage pattern shown in `test/webhooks/registry_test.rb` and `docs/usage/webhooks.md` — an attacker can cause actions to be attributed to, or performed against, another merchant's account (e.g. forging an `app/uninstalled` or order-mutation webhook against a victim shop) purely by controlling the headers of an HTTP POST to the app's webhook endpoint. This is a cross-tenant access primitive achieved without possessing the victim's credentials, satisfying the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires: (1) being any legitimate merchant with the vulnerable app installed (to obtain one validly HMAC-signed body/header pair), and (2) sending a crafted HTTP request to the app's public webhook endpoint with a different `shop-domain` header. No access to `api_secret_key`, tokens, or the victim's environment is needed, and the vulnerable code path (`Registry.process`) is the gem's documented, exact API for processing webhooks, so any app following the docs is exposed.

### Recommendation
Extend `to_signable_string`/`VerifiableQuery` for webhooks so the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`) are bound into the value that is HMAC-verified, or have `Registry.process` cross-check `request.shop` against an app-provided expected shop/session before dispatching to the handler. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be used as the sole tenant selector.

### Proof of Concept
1. Install the target app on shop `attacker.myshopify.com` and capture a real inbound webhook: raw body `B` and header `shopify-hmac-sha256: H` (valid because `H = HMAC_SHA256(client_secret, B)`, and `client_secret` is shared across all installs of the app).
2. Replay the request to the app's webhook endpoint, keeping body `B` and header `shopify-hmac-sha256: H` unchanged, but set `shopify-shop-domain: victim.myshopify.com` (and optionally forge `shopify-webhook-id`/`shopify-topic`).
3. `ShopifyAPI::Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` returns `true` because it only checks `B` against `H`.
4. `ShopifyAPI::Webhooks::Registry.process` in `lib/shopify_api/webhooks/registry.rb` (lines 188-200) builds `WebhookMetadata` with `shop: "victim.myshopify.com"` and dispatches to the app's handler, which acts as though the (attacker-controlled) payload legitimately originated from the victim's shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
