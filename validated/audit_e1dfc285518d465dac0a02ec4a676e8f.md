### Title
Webhook `shop` identity is not bound by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook purely by validating an HMAC computed over the raw request body, but the `shop` (and `topic`/`webhook_id`) values that the handler subsequently trusts and acts on are read from unauthenticated HTTP headers that are never included in the signed material. Because the `api_secret_key` used to compute this HMAC is the app's single client secret shared across every merchant/shop that has installed the app (not a per-shop secret), any unprivileged internet user who has installed the app on their own store can obtain a validly-signed webhook body and then replay it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header pointing at a victim shop. The HMAC check still passes because it never covered the shop header, so the handler will process the forged event as if it came from the victim tenant.

### Finding Description
Webhook authentication is implemented as: [1](#0-0) 

`Registry.process` only calls `Utils::HmacValidator.validate(request)` before dispatching to the handler with `request.shop`, `request.topic`, etc.

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For webhook `Request` objects, `to_signable_string` returns **only the raw body**: [3](#0-2) 

Meanwhile `shop`, `topic`, and `webhook_id` — the identity fields that determine *which tenant* the event belongs to — are parsed straight from HTTP headers with no cryptographic binding to the body or to each other: [4](#0-3) 

and are passed unchanged into the data handed to the host application's handler: [5](#0-4) 

The identity binding that should hold is:

`shop asserted to handler == shop that the HMAC-authenticated body actually originated from`

This equality is broken because the HMAC only proves *"this body was signed with the app's client secret at some point, for some shop"* — it says nothing about which shop's domain header may legitimately be attached to that body. Since `api_secret_key` is the same value for every shop that installs the app (it is the app's `client_secret`, not a per-merchant secret), any store owner who installs the app can capture a genuine, validly-HMAC'd webhook delivered to their own store, then POST that identical raw body to the app's public webhook endpoint while substituting `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) for a different, victim shop. `HmacValidator.validate` will still return `true` because it never looked at that header.

### Impact Explanation
This breaks the tenant isolation the gem is supposed to provide. Any application built on this library that uses `WebhookMetadata#shop` to select which merchant's session/data to mutate (the intended and documented usage pattern) can be tricked into applying attacker-controlled data to another shop's account — i.e., cross-tenant access/injection using only a webhook signed for the attacker's own shop. This satisfies the "Critical - cross-tenant access" impact bar since no privileged credential of the victim is required; the attacker only needs their own working installation of the app (an unprivileged, self-service action any developer/merchant can take) plus the ability to POST directly to the public webhook route.

### Likelihood Explanation
Likelihood is high: webhook endpoints are, by design, publicly reachable HTTP endpoints (see `docs/usage/webhooks.md`'s example Rails controller calling `Registry.process` on any inbound POST). Obtaining a legitimately-signed webhook body only requires installing the target app on an attacker-controlled development/trial store, which is normal, unprivileged behavior for any Shopify app. No access token, `api_secret_key` leak, or social engineering is needed — the attacker already legitimately possesses one correctly-signed `(body, hmac)` pair from their own store and merely changes an unauthenticated header on replay.

### Recommendation
Include the shop domain (and topic/webhook id, if they are meant to be trusted) in the signable material that the HMAC covers, or otherwise cryptographically bind the header value to the signed body before it is exposed to consumers via `WebhookMetadata`. At minimum, `Request#to_signable_string` should incorporate `shop-domain` (and ideally `topic`) so that `HmacValidator.validate` fails whenever these headers do not match what Shopify actually signed for that specific delivery.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, obtaining offline session access legitimately.
2. Shopify delivers a genuine webhook (e.g. `orders/create`) to the app's endpoint with a valid `X-Shopify-Hmac-Sha256` computed over the JSON body using the app's shared `api_secret_key`, and header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures the raw body and its valid HMAC value from this legitimate delivery (e.g. via request logging on infrastructure they control, or by triggering the webhook and observing it directly since it's their own store).
4. Attacker sends a new POST request directly to the app's public webhook route, re-using the same raw body and the same valid `X-Shopify-Hmac-Sha256` value, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses the forged header into `request.shop`. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (the raw body only) — this matches, so validation succeeds.
6. The host application's handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` and processes the attacker's data as if it originated from the victim shop.

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
