### Title
Webhook HMAC signature does not cover the `shop`/`topic` headers, allowing signed events to be replayed under a forged shop identity - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
This is a structural analog of the reported bug class: a field that the application acts on (the merchant/tenant identity) is not covered by the cryptographic check that is supposed to authenticate the message. In the Canto Identity report, the SVG line-splitting logic acted on byte offsets that were not consistently validated against the actual codepoint boundaries, producing output that diverged from what was "proven" correct. Here, `ShopifyAPI::Webhooks::Registry.process` treats a request's `shop` and `topic` headers as trustworthy tenant-identifying data, but the HMAC that is supposed to authenticate the whole webhook only signs the raw body, not those headers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

But `shop` and `topic` are read directly from unauthenticated request headers, independent of the body: [2](#0-1) 

`Registry.process` validates the HMAC over `to_signable_string` (i.e. only the body) and then, on success, forwards `request.shop` and `request.topic` — values that were never part of the signed material — directly to the app's handler as trusted tenant/event identity: [3](#0-2) 

`HmacValidator.validate` and `validate_signature` confirm the signed bytes are exactly `verifiable_query.to_signable_string`, with no reference to headers: [4](#0-3) 

The gem's own documentation instructs apps to key tenant-scoped work directly off `data.shop` from the handler callback: [5](#0-4) 

The binding that should hold is:
`HMAC-authenticated bytes == bytes the handler uses to determine tenant identity (shop) and event type (topic)`

Instead, the actual relationship is:
`HMAC-authenticated bytes == raw body only`, while `shop`/`topic` used for tenant routing come from headers outside that signature.

### Impact Explanation
Because Shopify apps share a single `client_secret` (`Context.api_secret_key`) across every installed shop (it's the app's credential, not a per-shop secret), any shop that has installed the app can receive genuine, correctly-HMAC-signed webhooks for its own store. An attacker who controls such a shop can capture one of these legitimate `(body, hmac)` pairs and replay it to the app's webhook endpoint with the `shop-domain` (and/or `topic`) header rewritten to reference a different, victim shop. `Utils::HmacValidator.validate` will still succeed, since it never inspects those headers, and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the victim tenant. Any handler that uses `data.shop` to look up sessions, write tenant-scoped records, or trigger tenant-scoped side effects (exactly as the shipped documentation recommends) processes an event as if it originated from a different merchant — a cross-tenant identity break driven entirely by this gem's webhook-validation contract.

### Likelihood Explanation
Exploitation requires only that the attacker control one shop that has installed the target app (an ordinary, unprivileged relationship to the app — no access to `api_secret_key`, no privileged account, and no interception of another tenant's traffic is needed). The attacker relies solely on their own genuine, Shopify-delivered webhook and a header rewrite against the app's own public endpoint.

### Recommendation
Include the header fields that the handler treats as authoritative (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) in the HMAC-signed material, or independently bind/verify them (e.g., look up the shop from an established session/installation record rather than trusting the header verbatim), so that `to_signable_string` covers every field the application subsequently acts on.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers an event (e.g. `orders/create`), receiving a legitimate webhook: body `B`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`, header `x-shopify-hmac-sha256: H` where `H = HMAC(secret, B)` per `lib/shopify_api/utils/hmac_validator.rb`.
2. Attacker resends the exact same `B` and `H` to the app's webhook route, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`B` only) and matches `H` — validation succeeds (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ..., ...)` and invokes the app's handler (`lib/shopify_api/webhooks/registry.rb:198`), which — per the documented pattern in `docs/usage/webhooks.md:26` — acts on `data.shop` as the victim tenant, even though the event body/content actually originated from the attacker's own shop.

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
