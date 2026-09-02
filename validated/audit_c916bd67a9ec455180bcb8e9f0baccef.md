### Title
Webhook `shop-domain` header is trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#hmac` and `to_signable_string` compute/verify the HMAC over only the raw request body, while `shop`, `topic`, `api_version`, and `webhook_id` are read from unauthenticated HTTP headers and passed straight through to the registered handler. This breaks the intended binding `shop_that_signed(hmac) == shop_used_by_handler`.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates the webhook solely via `Utils::HmacValidator.validate(request)`, which in turn calls `request.to_signable_string`. [1](#0-0) 

`Request#to_signable_string` returns only `@raw_body`, and `Request#hmac` decodes the `hmac-sha256` header. Meanwhile `Request#shop` simply reads the `shop-domain` header verbatim, with no cryptographic linkage to the HMAC computation at all: [2](#0-1) [3](#0-2) 

Because `HmacValidator.validate_signature` only recomputes `HMAC(secret, raw_body)` and compares it to the received `hmac` header, the validity of the signature is completely independent of the `shop-domain`, `topic`, `api-version`, and `webhook-id` headers. [4](#0-3) 

After successful HMAC validation, `Registry.process` builds `WebhookMetadata` directly from `request.shop` — the unauthenticated header value — and hands it to the app-registered handler as the tenant identity for that event: [5](#0-4) 

This means any two webhook deliveries that happen to have byte-identical raw bodies will produce a byte-identical, valid HMAC regardless of which headers (in particular `shop-domain`) accompany them. Any party who can obtain one valid `(raw_body, hmac)` pair for a given merchant/topic/secret (e.g., because they are a merchant of the same app and receive their own legitimate webhooks with the same secret, or because a body happens to collide across shops for topics with sparse/predictable/empty payloads such as `app/uninstalled`, `shop/redact`, or other minimal-body topics) can resubmit that same body with a different `shop-domain` header to the app's webhook endpoint. The HMAC will still validate because it never covered the shop field, and the handler will process the request believing it originated from the spoofed shop.

### Impact Explanation
If an app's webhook handler uses `WebhookMetadata#shop` to select which merchant's data/session/state to mutate (a very common pattern, e.g., to look up that shop's offline session and act on its resources), an attacker can cause the app to attribute or act on an event under the wrong shop identity — i.e., cross-tenant confusion/cross-tenant action — despite HMAC validation passing. This satisfies the "cross-tenant access" criterion for Critical/High impact classes in scope, because the gem's own signature-verification code (`Utils::HmacValidator`, `Webhooks::Request`) fails to bind the tenant-identifying field to the cryptographic proof it exposes to consuming applications as "verified."

### Likelihood Explanation
Likelihood is constrained by the fact that the gem's `Request` only guarantees the raw body is authentic for *some* shop under the app's shared `api_secret_key`; producing a colliding raw body for an *arbitrary* target shop requires either (a) topics whose payload is shop-independent/minimal (several mandatory/system topics have such payloads), or (b) capturing/replaying another tenant's raw webhook body while swapping only the header. Both are achievable by an unprivileged actor who is merely a merchant of the same app (no special credentials, no access token, no `client_secret` needed) and requires no code execution or bypass of TLS — only a legitimate webhook delivery.

### Recommendation
Include the identity fields (`shop-domain`, and ideally `topic`/`webhook_id`) in the value that is HMAC-verified, or otherwise require the consuming application to independently authenticate the shop domain (e.g. cross-check `request.shop` against a known/registered shop before trusting it), rather than exposing an unauthenticated header as though it were part of the verified payload. At minimum, `docs/usage/webhooks.md` and the `Webhooks::Request`/`WebhookMetadata` API should make explicit that `shop`, `topic`, `webhook_id`, and `api_version` are unauthenticated headers not covered by `HmacValidator.validate`, so host applications do not implicitly trust them as verified.

### Proof of Concept
1. App is subscribed to a webhook topic whose Shopify-generated payload is shop-independent or minimal, e.g. `app/uninstalled` with body `{}`.
2. Attacker (merchant A, a legitimate but unprivileged installer of the app) receives their own legitimate webhook delivery: `raw_body = "{}"`, `x-shopify-hmac-sha256 = HMAC(secret, "{}")`, `x-shopify-shop-domain = "shop-a.myshopify.com"`.
3. Attacker resends the exact same `raw_body` and `hmac` header to the app's webhook endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com` (a victim shop).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, "{}")` and matches the supplied hmac — validation passes.
5. `WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", ...)` is passed to the app's handler, which now believes this event genuinely originated from shop B, even though shop B never sent it. [5](#0-4)

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

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
