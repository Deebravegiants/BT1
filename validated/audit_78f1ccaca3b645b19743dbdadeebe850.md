### Title
Webhook `shop-domain`/`topic`/`webhook-id` headers are trusted as tenant identity but are not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop`, `topic`, `api_version`, and `webhook_id` values consumed by `ShopifyAPI::Webhooks::Registry.process` are read straight from unauthenticated HTTP headers. The HMAC therefore only proves "this body byte-sequence was produced with the app's secret" — it never binds the `shop-domain` header that the app's webhook handler uses as the tenant identifier.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

and `HmacValidator.validate`/`validate_signature` compute/compare the HMAC exclusively over that signable string: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled from headers with no cryptographic binding to the body: [3](#0-2) 

`Registry.process` validates the HMAC and then unconditionally forwards these unauthenticated header values — including `request.shop` — to the app's handler as the tenant/event identity: [4](#0-3) 

This is the exact identity-binding gap described in the analog bug class: a field that is *acted on* (`shop`, used by the host app to select which tenant's data/session the webhook applies to) is not covered by the HMAC that is supposed to authenticate the whole request, in the same way the original `DOMAIN_TYPEHASH` omitted `version` from the signed struct while the verifier still trusted the unsigned field.

Shopify apps normally share a single `api_secret_key` across every shop that has installed the app (the secret is per-app, not per-shop). Consequently, any shop that has legitimately installed the app can obtain a validly-signed `(body, HMAC)` pair for its own store, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header for a different, victim shop. `HmacValidator.validate` still succeeds (it only checks the raw body against the shared secret), and `Registry.process` will invoke the handler with `WebhookMetadata.new(topic: <attacker-chosen>, shop: <victim-shop>, body: <attacker-controlled-shaped-JSON>, ...)`, so the host application is handed fabricated, attributed-to-a-different-tenant webhook data with a supposedly-valid signature.

### Impact Explanation
An unprivileged holder of one valid app-installation (any shop that installed the app can obtain arbitrary genuinely-signed bodies, e.g. by triggering their own `orders/create` events) can forge webhook deliveries attributed to a different merchant/tenant. Because host applications key their per-tenant data lookups off `WebhookMetadata#shop` (the documented, intended purpose of this field), this enables cross-tenant data injection/corruption — writing or triggering actions against another shop's records — which maps to the "cross-tenant access" Critical impact category defined in scope.

### Likelihood Explanation
Exploitation requires only that the attacker's own shop has the app installed (an unprivileged, ordinary merchant relationship, no leaked secrets or privileged access needed) and the ability to send an HTTP POST with attacker-chosen headers to the app's public webhook endpoint — both are standard, low-effort capabilities for any app installer.

### Recommendation
Bind the tenant/topic identity into the signed material, e.g. include `shop`, `topic`, and `webhook_id` in `to_signable_string` (or otherwise incorporate them into the HMAC computation as Shopify's server-side webhook signing already covers the full canonical request), so that `HmacValidator.validate` fails whenever any of these header values are altered relative to what Shopify actually signed.

### Proof of Concept
1. App shop A (attacker-controlled, has the app installed) triggers a legitimate webhook event (e.g. `orders/create`); Shopify sends `POST /webhooks` with body `B` and header `X-Shopify-Hmac-Sha256: HMAC(secret, B)`, `X-Shopify-Shop-Domain: shop-a.myshopify.com`.
2. Attacker intercepts/replays this request to the same endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. `ShopifyAPI::Webhooks::Request#hmac`/`#to_signable_string` are computed solely from `B`; `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb:12-31` succeeds because the body byte content is unchanged.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: <attacker-controlled>, body: B, ...)`, causing the host application to process attacker-supplied data as if it originated from `victim-shop.myshopify.com`.

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
