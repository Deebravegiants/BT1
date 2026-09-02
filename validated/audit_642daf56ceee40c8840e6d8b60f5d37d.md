### Title
Webhook shop identity spoofing via unauthenticated `shop-domain` header not covered by HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` extracts the tenant identifier (`shop`) from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body, never the shop-domain header. `ShopifyAPI::Webhooks::Registry.process` trusts this unauthenticated header value and forwards it directly to the app's webhook handler as the shop the payload belongs to, breaking the binding between "bytes verified" (the raw body) and "shop acted on" (the header).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body or the HMAC: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC solely against `verifiable_query.to_signable_string` (i.e., the body), so it can never detect a header value that was altered post-signing: [3](#0-2) 

`Registry.process` validates the HMAC and then unconditionally passes `request.shop` into the app-level `WebhookMetadata`, which is exactly what the host app is told to trust as the tenant of the payload: [4](#0-3) 

The identity binding that should hold is: `hmac-verified body == payload attributed to shop X`. In this gem, the equality actually enforced is only `hmac-verified body == some body`; the shop label attached to that body is taken from an out-of-band header that carries no signature at all. Any party that can produce a validly-HMAC'd body for the app's client secret (which is shared across every shop that installs the app — e.g. an attacker who installs the app on their own shop and receives a genuine, correctly-signed webhook for that shop) can replay that exact body/HMAC pair while substituting an arbitrary `X-Shopify-Shop-Domain` header, and the gem will accept it and hand the (attacker-controlled) shop label to the handler as if Shopify had asserted it.

The library's own documentation reinforces the false assumption that HMAC validation guarantees full authenticity of the request, including the shop attribution: "This will verify the request did indeed come from Shopify," as shown in `docs/usage/webhooks.md` at the `Registry.process` example — but the shop-domain claim is not actually part of what's verified.

### Impact Explanation
This breaks the shop/tenant identity boundary the gem is supposed to enforce for host applications building multi-tenant Shopify apps: a webhook payload legitimately generated for shop B (an attacker's own store) can be relayed to the app's webhook endpoint labeled as belonging to shop A. Any host application that uses `WebhookMetadata#shop` to look up records, update state, or write data scoped to "shop A" (the standard, documented usage pattern shown in `docs/usage/webhooks.md`) will process attacker-supplied data under a different tenant's identity — a cross-tenant data injection/confusion primitive. This matches the Critical "cross-tenant access" impact category, since it is a violation of the tenant isolation the HMAC check is meant to guarantee.

### Likelihood Explanation
Exploitation only requires the ability to install the app on any shop (which is available to any unprivileged merchant/attacker for a public app) and to replay a captured request to the app's own publicly reachable webhook endpoint with a modified header — no access token, API secret, or privileged account is required. The `api_secret_key` itself is never exposed to the attacker; they only need one legitimately-signed webhook body from their own tenant, which Shopify sends them automatically once subscribed.

### Recommendation
Do not treat the `shop-domain` header as authenticated merely because the body HMAC validates. Either:
1. Include the shop domain (and other identity-relevant headers such as `webhook-id`/`api-version`) in the HMAC-signed material, or
2. Independently corroborate the shop by cross-referencing it against the webhook subscription registered with Shopify for that specific delivery (e.g., validate `webhook_id` against records already known to belong to that shop) before dispatching to the handler.

At minimum, update `docs/usage/webhooks.md` and the `WebhookMetadata#shop` contract to explicitly warn implementers that `shop` is not covered by the HMAC and must not be trusted for tenant-scoping decisions without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers for a webhook topic (e.g., `products/update`).
2. Shopify sends a legitimate webhook to the app's endpoint with headers:
   - `X-Shopify-Hmac-Sha256: <valid HMAC of body B>`
   - `X-Shopify-Shop-Domain: attacker.myshopify.com`
   - body `B` (attacker fully controls the resource content, e.g., product title/description).
3. Attacker replays the exact same request to the app's webhook endpoint, but rewrites the header to `X-Shopify-Shop-Domain: victim-shop.myshopify.com`, leaving body `B` and the HMAC signature untouched.
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) recomputes the HMAC over `B` only, finds it matches, and returns `true`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) proceeds to call the handler with `shop: "victim-shop.myshopify.com"` and `body: B`, even though Shopify never sent this payload for `victim-shop.myshopify.com`.
6. The host app's handler (per the documented pattern in `docs/usage/webhooks.md:19-29`) persists/acts on `data.body` scoped to `data.shop`, resulting in attacker-controlled data being written under the victim shop's tenant context.

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
