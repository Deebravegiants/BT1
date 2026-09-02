## Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
The webhook processing pipeline authenticates only the raw HTTP body via HMAC, but the `shop` (tenant) identity that gets handed to the application's webhook handler is read from an unauthenticated HTTP header. An attacker who legitimately receives one signed webhook for their own shop can replay the identical body + HMAC while substituting the `shop-domain` header, and the gem will accept it as coming from an arbitrary victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is instead read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string` (the raw body for webhooks) and compares it with `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` only calls this HMAC check, then forwards `request.shop` unchanged to the app's handler as the authoritative tenant identifier: [4](#0-3) 

This reproduces the report's bug class exactly: a field ("field acted on") — here the tenant/shop identity used to route and process the webhook — is not covered by the HMAC that authenticates the payload's origin. The equality that should hold is:

`shop_bound_by_signature == shop_used_for_tenant_processing`

but in this implementation `shop_bound_by_signature` is undefined (the signature covers body bytes only), while `shop_used_for_tenant_processing` is an attacker-controlled header value. Any holder of one validly-signed webhook (e.g., an attacker who installs the app on their own free/dev store and receives a real webhook from Shopify, signed with the app's shared `api_secret_key`) can resend that same body/HMAC pair with the `shop-domain` header changed to a victim shop's domain, and `HmacValidator.validate` will still return `true` because it never inspects the header.

### Impact Explanation
This breaks the tenant/identity binding for all HTTP webhooks processed through this gem: the "authenticated shop" and the "shop the handler acts on" are not the same value. Any consuming application that trusts `WebhookMetadata#shop` (as `Registry.process` explicitly hands it to `handler.handle`) to scope data writes/reads per-tenant can be tricked into applying another shop's webhook event (with attacker-controlled body content, since the attacker chose the original webhook topic/payload from their own store, or a topic whose body schema they can fully craft, e.g. `app/uninstalled`, `shop/update`) against a victim tenant's record — i.e., cross-tenant access, which the rules classify as Critical impact.

### Likelihood Explanation
Any user can register the app on their own store (unprivileged) and receive at least one legitimately signed webhook, satisfying the exploitation prerequisite without needing the `api_secret_key`, an access token, or any privileged account. Replaying with a modified header requires only basic HTTP tooling. This is the same class of exploit as sending a raw curl/HTTP request with attacker-controlled headers.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the material that is HMAC-verified, or otherwise cryptographically bind the header-derived `shop` value to the verified payload (e.g., look up the shop's own webhook signing behavior via Shopify's per-shop metadata, or require the app layer to cross-check `shop` against a known registration before trusting it). At minimum, document prominently that `request.shop` is unauthenticated and must not be used as a sole tenant-scoping key without additional verification (e.g., verifying the shop is one that has an active session/installation, and rejecting mismatches from previously known good values).

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and triggers a real webhook (e.g., `orders/create`), capturing the raw body `B` and the resulting `x-shopify-hmac-sha256` header `H` — both legitimately produced by Shopify using the app's `api_secret_key`.
2. Attacker sends a new HTTP request to the app's webhook endpoint with:
   - body = `B` (unchanged)
   - `x-shopify-hmac-sha256` = `H` (unchanged)
   - `x-shopify-shop-domain` = `victim.myshopify.com` (changed)
   - `x-shopify-topic` = same or different registered topic
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and matches `H` → validation passes. [5](#0-4) 
4. `handler.handle` is invoked with `WebhookMetadata` where `shop == "victim.myshopify.com"`, even though Shopify never sent this webhook for that shop. [6](#0-5)

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
