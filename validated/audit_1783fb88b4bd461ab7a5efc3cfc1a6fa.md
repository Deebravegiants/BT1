### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant impersonation via replayed webhook bodies - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented to "verify the request did indeed come from Shopify" before invoking the app's handler with a `WebhookMetadata` struct that includes `shop` as the tenant identifier [1](#0-0) . In reality, the HMAC only covers the raw request body, while `shop` is taken verbatim from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts `shop` directly from an HTTP header with no cryptographic binding to the signed content: [2](#0-1) 

`to_signable_string` — the only material fed into the HMAC check — returns solely `@raw_body`, never the headers: [3](#0-2) 

`Registry.process` validates that HMAC and then, without any additional check that `request.shop` matches anything covered by the signature, forwards the header-derived `shop` straight into `WebhookMetadata`, which is the value app handlers use as the trusted tenant identifier: [4](#0-3) 

The binding that should hold is:
`hmac_signed_bytes == bytes_that_determine(shop_used_for_authorization)`

but the actual state is:
`hmac_signed_bytes == raw_body` while `shop_used_for_authorization == unauthenticated_header`

Because the two are disjoint, `HmacValidator.validate` only proves "this exact body byte-string was HMAC'd with the app secret at some point" — it proves nothing about which shop sent it [5](#0-4) . `HmacValidator.validate_signature` similarly only compares `verifiable_query.to_signable_string` (the body) against `hmac`, never any header value [6](#0-5) .

Any unprivileged internet user who can install the app on their own store (or otherwise legitimately trigger one real webhook delivery) obtains a `(raw_body, valid_hmac)` pair signed with the app's shared `api_secret_key`. That pair is not shop-specific — the shop identity lives only in a header that isn't part of what was signed. The attacker can POST that exact same `raw_body` with the same `hmac` header to the app's webhook endpoint again, but substitute an arbitrary `shopify-shop-domain` header (e.g., a victim shop or an internal test domain). `Registry.process` will still pass HMAC validation and will hand the handler a `WebhookMetadata` claiming the payload originated from the attacker-chosen shop [7](#0-6) .

### Impact Explanation
This is a cross-tenant identity confusion in the gem's own webhook verification primitive: the `shop` field that this library hands to the application as "the shop the verified webhook is for" is not actually verified. Any host application that follows the documented contract (using `data.shop` from a `process`-validated request as the tenant key, e.g. to look up store-scoped credentials, write into per-shop data stores, or route background jobs) can be made to process attacker-controlled webhook content under a victim's tenant identity. This satisfies the Critical bar of "cross-tenant access" since the trust boundary crossed is exactly the one the gem's `process` method purports to enforce.

### Likelihood Explanation
Exploitation requires no privileged credentials: an attacker only needs to be able to trigger one webhook delivery for their own low-privilege shop (installing any public/dev app is inherently unprivileged and self-service), capture the `(raw_body, hmac)` pair, and replay it with a forged `shop` header at the app's public webhook endpoint. No knowledge of `api_secret_key` is needed because the attacker reuses a signature Shopify already computed for them.

### Recommendation
Bind `shop` into the material that is HMAC-verified, or otherwise cryptographically authenticate the header before trusting it — e.g., require callers to additionally verify `shop` against a known/registered shop list keyed by data that *is* signed (such as content embedded in the body), or extend `to_signable_string` semantics so `HmacValidator` can express "this body may only be attributed to shop X" rather than leaving header-derived identity entirely outside the signature. At minimum, document loudly in `docs/usage/webhooks.md` and in `WebhookMetadata`/`Request#shop` that `shop` is NOT covered by `hmac` validation and must not be used as an authorization/tenant key without an independent, out-of-band check.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers any subscribed webhook topic (e.g. `orders/create`), capturing the raw POST: body `B` and header `x-shopify-hmac-sha256: H` (valid because Shopify signed `B` with the app's real `api_secret_key`).
2. Attacker replays the request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` parses successfully; `shop` returns `"victim-shop.myshopify.com"` [8](#0-7) .
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H`, so validation passes [9](#0-8) .
5. The registered handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, believing the (attacker-controlled) payload `B` is a genuine event for the victim shop, despite `B` never having originated from or been signed on behalf of that shop.

### Citations

**File:** docs/usage/webhooks.md (L123-135)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
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
