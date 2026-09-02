This confirms the vulnerability. The `x-shopify-shop-domain` header is explicitly documented as part of the trusted webhook data contract but is never covered by the HMAC signature.

### Title
Webhook shop-domain spoofing enables cross-tenant webhook injection - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while `ShopifyAPI::Utils::HmacValidator.validate` accepts the request as authentic once that body-only HMAC matches. The `shop` value (read from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header) is then passed straight into `WebhookMetadata` and handed to the host app's handler as the authoritative tenant identifier, even though it was never part of the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 
so only `@raw_body` is signable. The `shop`, `topic`, `api_version`, and `webhook_id` are all read from headers that are excluded from the signature: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (the body only) using the app's single, shop-independent `Context.api_secret_key`: [3](#0-2) 

`Webhooks::Registry.process` trusts this validation and then forwards `request.shop` — the unauthenticated header value — directly to the handler as the tenant identifier: [4](#0-3) 

Because the HMAC secret (`api_secret_key`) is the same for every shop that installs the app, any legitimate webhook received by *any* shop that has installed the app yields a valid `(raw_body, hmac)` pair signed with the same secret used for all tenants. That pair remains valid regardless of which `shop-domain` header accompanies it, since the header is not part of the signed content. The binding the app relies on — "the shop attested by the signature" == "the shop the payload is attributed to" — does not actually exist; the signature only proves "signed by this app's secret," not "originated for this shop."

The documentation confirms host apps are expected to trust `data.shop` for tenant-scoped processing (e.g., `perform_later(shop_domain: data.shop, ...)`): [5](#0-4) 

### Impact Explanation
An attacker who has installed the app on their own (attacker-controlled) shop receives legitimate webhooks with valid HMACs for arbitrary payload content they can influence (e.g., by editing a product, order, or other resource to produce a chosen body). By replaying that `(raw_body, hmac)` pair to the app's shared webhook endpoint while substituting the `x-shopify-shop-domain` header for a different, victim shop, the attacker causes the host application to process attacker-crafted data under another tenant's identity. Since host apps built on this documented contract key their persistence, business logic, and side effects (billing, inventory, order state, notifications) by `data.shop`, this enables cross-tenant data injection/corruption — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any developer/merchant can install the target app for free/trial to become a legitimate, unprivileged webhook sender for their own shop, and the webhook endpoint is by design a public HTTP endpoint that must accept unauthenticated Shopify-origin traffic. No secrets beyond a body+hmac pair the attacker can legitimately obtain are required, and the header spoofing requires only unrestricted HTTP client access.

### Recommendation
Bind the shop domain (and ideally topic/api_version/webhook_id) into the signed content the gem verifies, or otherwise cryptographically tie the header values to the signature — e.g., include them in `to_signable_string`, or require the host app to verify that `request.shop` matches a shop for which a webhook with this exact topic/id was actually registered before trusting it. At minimum, document prominently that `request.shop` is not authenticated by the HMAC and must not be trusted as a tenant boundary without additional verification (e.g., cross-referencing against `webhook_id` records stored at registration time).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` (normal, unprivileged onboarding).
2. Attacker triggers a real webhook (e.g. `orders/create`) by placing an order, receiving body `B` and a valid `x-shopify-hmac-sha256` header `H` signed with the app's `api_secret_key` (shared across all tenants).
3. Attacker crafts a raw HTTP POST to the app's public webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged request; `Utils::HmacValidator.validate` recomputes HMAC over `B` only and it matches `H`, so validation passes (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. `Webhooks::Registry.process` invokes the host app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the app to process attacker-controlled data as belonging to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
