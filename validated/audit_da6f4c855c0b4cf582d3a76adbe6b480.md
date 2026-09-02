### Title
Webhook `shop`/`topic`/`webhook_id` identity headers are trusted as authenticated even though the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` (invoked from `Registry.process`) authenticates *only the body bytes*. The `shop-domain`, `topic`, `webhook-id`, and `api-version` HTTP headers are never part of the signed material, yet `Registry.process` treats `request.shop` and `request.topic` as authenticated tenant/routing identifiers and forwards them unchanged to the host app's handler via `WebhookMetadata`.

### Finding Description
The equality the gem implicitly claims to guarantee is:

`bytes verified by HMAC == bytes the handler trusts as this webhook's identity`

In practice:
- Verified side: `to_signable_string` → `@raw_body` only [1](#0-0) .
- Trusted/acted-on side: `shop`, `topic`, `webhook_id`, `api_version` are all pulled straight from unauthenticated headers [2](#0-1) .
- `Registry.process` gates on `Utils::HmacValidator.validate(request)` — which only checks the body — and then unconditionally builds `WebhookMetadata` from the unauthenticated header-derived `shop`/`topic`/`webhook_id`, passing that struct to the app's registered `WebhookHandler#handle` as if it were verified data [3](#0-2) .

Because `Context.api_secret_key` is a single, app-wide secret shared across every shop that has installed the app (there is no per-shop signing key), any `(raw_body, hmac)` pair that is valid for one tenant/topic is *also* a cryptographically valid pair for every other tenant/topic — nothing in the signed bytes binds the message to a particular `shop` or `topic`. Once such a pair is available, it can be re-submitted to the same public webhook endpoint with different `shopify-shop-domain` / `shopify-topic` header values, and `HmacValidator.validate` will still return `true`, because it never inspects the headers at all [4](#0-3) . The gem then hands the app a `WebhookMetadata` whose `shop` field says "this event belongs to tenant X" purely on the strength of an unauthenticated header, despite the caller believing the entire message — including its tenant attribution — was HMAC-verified.

This is the same class of defect as the report's core issue: a value that is *used* to drive downstream state (there: shares burned per claim; here: which tenant's data the event is attributed to) is computed/derived from data that falls outside the mechanism meant to guarantee its integrity (there: `netReturn` outside the real accrual; here: `shop`/`topic` headers outside the HMAC digest).

### Impact Explanation
Host applications built on this gem's documented webhook flow (`Registry.process`) receive a `WebhookMetadata.shop` value that they are entitled to treat as authenticated, since the gem's own contract is "HMAC validated → safe to process." In a multi-tenant app, this field is commonly used directly as a lookup/session key or to scope which merchant's records get written. Because the signature never binds `shop`/`topic` to the body, a captured or replayed webhook can be attributed to an arbitrary tenant, enabling cross-tenant data confusion/injection without needing the app's `client_secret`, an access token, or any privileged credential — only a single previously-valid `(raw_body, hmac)` pair for the shared app secret. This maps to the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one legitimately HMAC-signed `(raw_body, hmac)` pair — which is trivially available to any unprivileged merchant that has installed the app on their own store, since every webhook Shopify delivers to the app for that merchant's own shop is signed with the same app-wide secret. No interception of Shopify's or the app's TLS traffic is required to obtain this pair; the merchant is a legitimate recipient-adjacent party of their own webhook traffic (e.g., via their own logging/tunnel tooling on their own install) and can then submit the captured body+hmac directly to the app's public webhook endpoint with altered `shop-domain`/`topic` headers.

### Recommendation
Bind the identity headers into the signed material instead of trusting them out-of-band: include `shop`, `topic`, and (if used for idempotency/dedup) `webhook_id`/`api_version` in `to_signable_string`, or otherwise cryptographically bind them (e.g., derive an HMAC over `shop|topic|raw_body`). At minimum, document that `HmacValidator.validate` only authenticates the body and that host applications must independently verify `shop` against their own known/installed shop list and `topic` against the topic they registered that endpoint for before trusting `WebhookMetadata`.

### Proof of Concept
1. As an unprivileged merchant, install the target app on your own dev/test shop (`shop-A.myshopify.com`) and trigger any subscribed webhook topic (e.g. `products/update`) so Shopify delivers a signed request to the app's public webhook endpoint. Capture the raw request body and the `X-Shopify-Hmac-Sha256` header value from your own tooling in front of your own install (e.g., request logging/tunnel proxy you control for your own store's webhook traffic).
2. Independently send a new HTTP request directly to the app's public webhook endpoint using:
   - the identical `raw_body` and `X-Shopify-Hmac-Sha256` value captured in step 1,
   - a forged `X-Shopify-Shop-Domain` header naming a different, unrelated shop (`shop-victim.myshopify.com`),
   - the same or different `X-Shopify-Topic` header.
3. Observe that `ShopifyAPI::Webhooks::Registry.process` accepts the request because `Utils::HmacValidator.validate(request)` only re-computes the HMAC over `raw_body` [5](#0-4)  and passes, then dispatches `handler.handle` with `WebhookMetadata.shop == "shop-victim.myshopify.com"` and the attacker's captured body content [6](#0-5)  — confirming the tenant attribution is unauthenticated despite HMAC validation "passing".

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
