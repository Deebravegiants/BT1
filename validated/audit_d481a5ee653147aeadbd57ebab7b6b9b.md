I have sufficient evidence to confirm the analog vulnerability. Here is the finding:

### Title
Webhook shop-domain identity not covered by HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (tenant identity), `topic`, `webhook_id`, and `api_version` values used by `ShopifyAPI::Webhooks::Registry.process` and passed to the app's `WebhookHandler` are taken from unauthenticated HTTP headers that are never part of the signed bytes. This breaks the identity binding `hmac-verified-bytes == data-acted-upon`, analogous to the reported DAO bug class where a field acted on (tenant/shop) is not covered by the binding check (HMAC) that is supposed to authenticate the request.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers, independent of the signature: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which only checks `to_signable_string` (the body) against the `hmac` header, and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `to_signable_string`: [4](#0-3) 

Because the shop-domain header is excluded from the signed bytes, the equality the gem is supposed to enforce — "the shop the HMAC authenticates" == "the shop the handler acts on" — does not hold. Any request carrying a body/HMAC pair that validates (e.g., a previously captured legitimate webhook payload for one shop, or any body Shopify signs) can have its `shopify-shop-domain` / `x-shopify-shop-domain` header freely rewritten by a man-in-the-middle-free replaying party without invalidating the HMAC check, since that header is never part of `to_signable_string`. The Ruby gem's documented usage pattern explicitly forwards `data.shop` to downstream job/session logic (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`), so host applications following the gem's own documentation will key tenant-scoped work off this unauthenticated field: [5](#0-4) 

This mirrors the reported bug class: a binding meant to authenticate the actor/tenant (the recovery-mode membership check bound to `msg.sender`/registered node) is bypassed because a related field used downstream (DAO membership decision) is not actually covered by the enforcement the system relies on. Here, the enforcement (`HmacValidator.validate`) covers only body bytes, not the shop identity field that downstream tenant-scoped logic consumes.

### Impact Explanation
This falls under "scope check bypass" / identity-binding break at High severity: a party who has captured or otherwise has a valid `(raw_body, hmac)` pair for one shop can relabel the same payload with a different `x-shopify-shop-domain` header and have it processed by the app as if it originated from a different tenant. Since the app's own webhook handler receives `WebhookMetadata#shop` as an authenticated fact (it passed `HmacValidator.validate`), and the gem's documentation instructs developers to key `shop_domain`-scoped background work directly off this value, an attacker can cause cross-tenant data confusion/write in host applications that trust `data.shop` as validated.

### Likelihood Explanation
Likelihood is constrained by the fact that computing a valid HMAC over an arbitrary body still requires the app's `client_secret`/`api_secret_key`, which the gem correctly does not expose to unprivileged attackers. However, a captured legitimate webhook delivery (which is visible on the wire to anyone able to observe or replay HTTP traffic to the app's public webhook endpoint, e.g., via logs, proxies, or the endpoint itself echoing/relaying the body) is sufficient to exploit this, because the shop header can be swapped without needing the secret at all — the vulnerability is specifically that the header is decoupled from the signature that is meant to authenticate it.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id/api-version) header values in the bytes covered by the HMAC verification, or otherwise cryptographically bind them to the signed payload, so that `HmacValidator.validate` fails if any of these identity-bearing headers are altered relative to what Shopify originally signed. At minimum, document loudly that `data.shop` in `WebhookMetadata` is not itself authenticated by the HMAC check and must not be used as a sole tenant key without additional verification (e.g., cross-checking against a known registered shop/session store).

### Proof of Concept
1. Obtain a legitimate webhook body/HMAC pair sent by Shopify for `shop-a.myshopify.com` (e.g., via network logging, a shared proxy, or any component with sight of the raw request).
2. Replay the identical `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but substitute `x-shopify-shop-domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `Digest.hexencode(...)` against `OpenSSL::HMAC.hexdigest(sha256, secret, raw_body)` — unaffected by the header change — so it returns `true`: [6](#0-5) 
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built using the attacker-controlled `shop-b.myshopify.com` value and passed to the app's handler as an "authenticated" webhook for `shop-b`: [7](#0-6)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
