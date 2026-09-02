I have sufficient evidence to confirm the vulnerability. The `Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC computed by `HmacValidator.validate` [1](#0-0)  never covers the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers, yet `Registry.process` passes `request.shop` straight into the handler as the tenant identity [2](#0-1) .

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
The bug-class hint (unsafe cast producing a value that doesn't match what it's supposed to represent) analogizes here to a field that is *used* as an authenticated identity value but is *not actually covered by the cryptographic check* — the classic "verified bytes vs. parsed/acted-on bytes" mismatch called out in the rules.

### Finding Description
`ShopifyAPI::Webhooks::Request` derives `shop` (and `topic`, `webhook_id`, `api_version`) purely from HTTP headers: [3](#0-2) 

Its `to_signable_string`, which is the exact byte string handed to `HmacValidator.validate` for HMAC-SHA256 verification, returns only `@raw_body`: [4](#0-3) 

`HmacValidator.validate_signature` computes `HMAC(secret, request.to_signable_string)` and compares it to the `hmac-sha256`/`x-shopify-hmac-sha256` header value using `OpenSSL.secure_compare`: [1](#0-0) 

`Registry.process` then dispatches directly on `request.topic` and forwards `request.shop` unchanged to the app's `WebhookHandler` as the trusted tenant identifier: [5](#0-4) 

**Identity binding that should hold:** `shop_bound_by_hmac == shop_delivered_to_handler`.
**What actually holds:** the HMAC only binds `raw_body`; `shop-domain` (and `topic`/`webhook-id`/`api-version`) are unauthenticated, attacker-controllable request metadata forwarded verbatim to the handler. So the equality the code implicitly relies on — "the HMAC-verified request came from shop X" — does not hold; only "the body bytes were HMAC'd by *some* valid webhook, for *some* shop" holds.

Because Shopify signs webhooks per-app (same `api_secret_key` for every shop/merchant using that app), any unprivileged actor who can install/operate the app on **their own** store legitimately receives genuine webhooks with valid HMACs for their own shop's body content. Nothing in this library prevents them from replaying that exact `raw_body` + `hmac-sha256` value to the app's webhook endpoint while substituting an arbitrary `shop-domain` header (e.g., a victim merchant's domain). `HmacValidator.validate` still returns `true` because the body/HMAC pair is unchanged and valid; `Registry.process` then invokes the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

### Impact Explanation
This is a cross-tenant identity confusion: the handler, and by extension the host application's per-shop data store, is told that data controlled by the attacker actually belongs to a different (victim) shop, purely because `shop-domain` is unauthenticated. Depending on how the host app keys data/actions by `WebhookMetadata#shop`, this can let an attacker inject or overwrite records attributed to a shop they do not control (cross-tenant access), satisfying the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Likelihood is High for any unprivileged internet user: they only need to be a legitimate (even free-tier) installer of the same app on their own store to obtain a validly HMAC'd webhook body/signature pair, then replay it with a forged `shop-domain` header — no access to `api_secret_key`, access tokens, or the victim's credentials is required, and no TLS interception or social engineering is involved.

### Recommendation
Include the shop identity (and ideally topic/webhook-id) in the HMAC-covered signable string, or otherwise cryptographically bind the `shop-domain` header to the signed payload before trusting it in `Registry.process`/`WebhookMetadata`. At minimum, cross-check `request.shop` against the shop associated with the session/install record that the app expects for that webhook subscription, rather than trusting the header value as-is.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged install).
2. Shopify sends a genuine webhook to the app: body `{"id":1,...}`, header `x-shopify-hmac-sha256: <valid HMAC of that body>`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged header into `shop`; `HmacValidator.validate(request)` succeeds because it only hashes `@raw_body`, per `to_signable_string` at `lib/shopify_api/webhooks/request.rb:35-38`.
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(... shop: request.shop ...)` where `shop` is `"victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
