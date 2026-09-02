### Title
Webhook shop identity is not bound to the HMAC signature, allowing cross-tenant webhook spoofing — (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the shop identity (`shop-domain` header) that the gem hands to the app's webhook handler as the trusted tenant identifier is taken from an unsigned header. This breaks the equality that should hold: `hmac_verified_bytes == bytes_the_handler_trusts_for_tenant_identity`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers that are not part of the signed content: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then forwards `request.shop` unchecked to the app's handler as the authoritative tenant identifier: [3](#0-2) 

The documentation instructs host apps to treat `data.shop` as the shop the webhook came from and to route/queue work keyed on it (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`): [4](#0-3) 

Because the Shopify app's `api_secret_key` is a single shared secret used to sign webhooks for *every* shop that installs the app (not a per-shop secret), any shop that installs the app can legitimately receive a validly-signed webhook for its own shop. That shop owner can then replay the same body/HMAC pair while substituting a different `X-Shopify-Shop-Domain` header value. Since the header is excluded from `to_signable_string`, `HmacValidator.validate` still succeeds, and `Registry.process` passes the attacker-chosen `shop` value straight through to the handler as if it were verified — this is the same class of bug as the reference finding: an identifying field (`vault`/`shop`) that is acted upon by downstream logic is never bound to the value that was actually authenticated (`proposalId`/HMAC digest).

### Impact Explanation
An app that uses `data.shop` from `WebhookMetadata` to select which tenant's data to update, queue background jobs against, or which access token to look up, can be tricked into applying an attacker's payload under a victim shop's identity — a cross-tenant confusion. This matches the Critical "cross-tenant access" impact category, since the gem itself supplies an unverified tenant identifier under the label of a verified request.

### Likelihood Explanation
No special credentials beyond installing the app as an ordinary merchant are required (any shop's own valid webhook satisfies the HMAC check). Attack only requires editing the `X-Shopify-Shop-Domain`/`shopify-shop-domain` header and replaying the request, no access token or `client_secret` leakage needed.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) header values in the signable string, or otherwise cryptographically bind them to the HMAC, so `HmacValidator.validate` fails if any of these fields are altered independently of the signature. Alternatively, `Registry.process`/`WebhookMetadata` should not present `shop` as trusted unless it has itself been covered by the signature.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and receives a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: HMAC(secret, B)`, `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends the exact same body `B` and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `HmacValidator.validate` in `hmac_validator.rb` recomputes HMAC over `@raw_body` only (`to_signable_string` at `request.rb:35-38`) — it matches, so validation passes.
4. `Registry.process` (`registry.rb:188-199`) calls the app handler with `WebhookMetadata(shop: "victim.myshopify.com", body: B, ...)`, i.e., attacker-controlled body attributed to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
