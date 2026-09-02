### Title
Webhook `shop` field is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the `shop` (and `topic`, `api_version`, `webhook_id`) values are read from unauthenticated HTTP headers. `Utils::HmacValidator` validates the HMAC against only the body, so the `shop` value that is trusted and acted upon by `Registry.process` is never cryptographically bound to the signature. This is the classic HMAC-signed-body-vs-unsigned-header pattern from the rules: a field acted on (`shop`) but not covered by the HMAC.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is pulled straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no relation to the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` recomputes the HMAC purely from `to_signable_string` (the body) and compares it to the `hmac-sha256` header, so it never inspects the `shop` header at all: [3](#0-2) 

`Registry.process` then trusts this unauthenticated `shop` value and passes it straight into the handler's `WebhookMetadata`: [4](#0-3) 

Because the app's `api_secret_key` is shared across every shop that has the app installed, any merchant who installs the app receives genuine webhooks with a valid HMAC computed over a body they fully control the shape of (e.g., they can trigger `shop/redact`, `customers/redact`, `orders/create`, etc. from their own store). Since the header carrying `shop` is excluded from the signed content, that attacker can capture one legitimately-signed `(body, hmac)` pair from their own store's webhook delivery and replay it to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to a victim shop's domain. The signature still validates (it only checks the body), and the handler executes with `WebhookMetadata.shop` set to the victim's shop — a cross-tenant identity binding break: `shop_authenticated_by_hmac == "" ` while `shop_used_by_handler == attacker_chosen_value`.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to guarantee. A single-tenant attacker (any merchant who installs the app) can forge webhook deliveries that the app processes as if they originated from an arbitrary victim shop, without possessing that shop's credentials. Depending on the registered handlers (e.g., mandatory compliance topics like `customers/data_request`, `customers/redact`, `shop/redact`, or app-specific business-logic topics), this can lead to cross-tenant data corruption, unauthorized redaction, or business logic being executed against a shop the attacker does not control — meeting the Critical "cross-tenant access" bar.

### Likelihood Explanation
Likelihood is High: the attacker only needs to be a legitimate (but unprivileged) merchant with the app installed on their own store to receive a validly-signed webhook body/HMAC pair, and no secrets, tokens, or elevated access are required to replay it with a rewritten `shop` header against the app's public webhook endpoint.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`) values as part of the signed content that `to_signable_string` returns, or otherwise cryptographically bind them to the HMAC before trusting them in `Registry.process`. Since Shopify's HMAC is computed by Shopify only over the raw body per their webhook spec, the gem should instead treat the header-derived `shop` as untrusted unless independently corroborated (e.g., cross-checked against a known/installed-shop list) before being handed to application handlers.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook event (e.g. `customers/data_request`) that Shopify delivers to the app's webhook endpoint with a valid `X-Shopify-Hmac-Sha256` header computed over the raw JSON body using the shared `api_secret_key`.
2. Attacker captures the raw body and the `hmac-sha256` header value from that delivery.
3. Attacker replays an HTTP POST to the same webhook endpoint, keeping the raw body and `hmac-sha256` header identical, but replaces the `shopify-shop-domain` header with `victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only recomputes the signature over `request.to_signable_string` (the unchanged raw body).
5. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) invokes the registered handler with `WebhookMetadata.shop == "victim.myshopify.com"`, even though the request never originated from Shopify on behalf of that shop.

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
