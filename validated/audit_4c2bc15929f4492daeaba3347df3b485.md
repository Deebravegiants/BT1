Found a concrete identity-binding break: the webhook `shop` used by `Webhooks::Registry.process` is taken from the `X-Shopify-Shop-Domain` header, which is not covered by the HMAC signature.

### Title
Webhook `shop` value is trusted from an HTTP header not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verified in `Registry.process` binds solely to the body bytes. The `shop` value passed downstream to the app's webhook handler comes from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never included in the signed payload.

### Finding Description
`Request#hmac` is derived from the `hmac-sha256` header and `to_signable_string` returns `@raw_body` only: [1](#0-0) 
`Request#shop` simply reads the `shop-domain` header with no cryptographic binding to the body or hmac: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e., over the body only), then immediately trusts `request.shop` (from the unverified header) to build the `WebhookMetadata` passed to the host app's handler: [3](#0-2) 

The identity binding the code should guarantee is:
`hmac == HMAC(secret, body || shop || topic)` such that the `shop` acted upon is covered by the same signature that authenticates the request. Instead the code only checks `hmac == HMAC(secret, body)`, while `shop` (and `topic`, `webhook_id`) are read from unauthenticated bytes. This matches the report's bug class: "a field acted on but not covered by the HMAC" / "bytes verified versus bytes parsed" — here the bytes verified (raw body) differ from the bytes parsed for tenant identity (`shop-domain` header).

Because a valid HMAC only proves that *some* legitimate Shopify webhook body was sent for *some* shop the app is installed on (i.e., an app receives genuine webhooks from many different merchant shops it serves, each with a body signed using the same shared `api_secret_key`), an attacker who can capture or replay one legitimate webhook body/HMAC pair from their own (attacker-controlled) shop installation can resend it with a forged `X-Shopify-Shop-Domain` header pointing at a different, victim shop. `Registry.process` will pass HMAC validation (since it only checks the body) and dispatch the handler with `shop: <victim-shop>`, `topic`, and `webhook_id` all taken from attacker-controlled headers.

### Impact Explanation
This is a cross-tenant data/authorization confusion inside the gem's own webhook dispatch path: the `shop` identity handed to `WebhookHandler#handle` is not bound by the same signature that authenticates the payload, so an attacker holding one valid (own-shop) webhook body+HMAC can make the library assert it belongs to a different shop. Any host application that relies on `WebhookMetadata#shop` (as returned by this gem) to select which merchant's data/session to act on — exactly the intended use per the gem's own `docs/usage/webhooks.md` — can be tricked into cross-tenant actions (e.g., processing a `customers/redact` or `orders/*` payload under the wrong shop, or looking up/mutating the wrong merchant's session/access token by the spoofed shop). This satisfies the Critical "cross-tenant access" impact category, since the boundary crossed is the tenant (shop) identity used for all subsequent data operations, and it is exploitable by anyone who can deliver an HTTP request to the app's public webhook endpoint plus a valid HMAC of the body for any shop signed with the app's shared secret (which every legitimately installed shop can produce, since `X-Shopify-Hmac-Sha256` is derived using the app's single `client_secret`, not a per-shop secret).

### Likelihood Explanation
Likelihood is High for any multi-tenant app: the attacker only needs to install the app on one shop they control, capture a legitimate webhook (body + HMAC), and replay the identical body/HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header. No secret, access token, or privileged access is required beyond controlling one shop's app installation, which is the normal unprivileged-merchant path.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) into the signed material verified by `HmacValidator`, e.g., by including the `shop-domain` header value in `to_signable_string`, or independently re-deriving/confirming the `shop` from a value inside the verified request body (Shopify webhook payloads generally do not include the shop domain in the body, so this requires either an out-of-band per-shop secret check or requiring the host app to independently verify the shop is one it has an active session/installation for before trusting the `shop` value returned by this gem).

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com`; trigger any webhook (e.g., `orders/create`) and capture the raw request body and the `X-Shopify-Hmac-Sha256` header sent by Shopify.
2. Replay an HTTP POST to the app's webhook endpoint with the identical body and `X-Shopify-Hmac-Sha256` header, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and `X-Shopify-Topic`/`X-Shopify-Webhook-Id` as desired.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds `shop` from the (forged) header [2](#0-1) .
4. `Utils::HmacValidator.validate(request)` succeeds because it only re-computes HMAC over `@raw_body`, which is unchanged [4](#0-3) .
5. `Registry.process` invokes the app's handler with `shop: "victim-shop.myshopify.com"`, `topic`, `webhook_id`, and `body` all attacker-controlled beyond the raw body content [3](#0-2) , causing the host app (if it trusts this metadata, as the gem's design intends) to act as though the event pertains to `victim-shop`.

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
