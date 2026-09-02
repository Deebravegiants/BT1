### Title
Webhook `shop` (and `topic`/`webhook-id`) identity fields are not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the webhook HMAC over the raw request body only, while the merchant-identifying `x-shopify-shop-domain` (and `x-shopify-topic`/`webhook-id`) headers are read separately and forwarded, unauthenticated, to the app's webhook handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` (and `#topic`, `#webhook_id`) are read straight from the HTTP headers with no cryptographic binding to the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.hmac` against `verifiable_query.to_signable_string`, i.e. the body, never the shop header: [3](#0-2) 

`Registry.process` accepts the request once the body HMAC checks out, and forwards `request.shop` (the unauthenticated header) directly to the app's registered handler as the tenant identity for the event: [4](#0-3) 

Because the app's `client_secret`/`api_secret_key` is a single shared secret used for every shop that installs the app (not a per-shop secret), any body+HMAC pair that is valid for one tenant's webhook delivery is *also* a cryptographically valid signature for every other tenant, since the shop identity is not part of the signed material. An attacker who operates their own shop that has this app installed can capture one of their own legitimately-delivered webhook payloads (body + `x-shopify-hmac-sha256`), then re-POST that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` will still pass (it only checks the body against the shared secret), and `Registry.process` will invoke the app's handler with `shop: <victim shop>`, causing the app to process attacker-controlled webhook data under another tenant's identity.

This is the direct analog of the reported bug class: a value the system *acts on* (here, the tenant-identifying `shop` field, analogous to the collateral/liquidation account identity) is not bound by the authentication mechanism (here, HMAC, analogous to a collateralization check) that is otherwise trusted to establish integrity of the request.

### Impact Explanation
This breaks the identity binding `authenticated_bytes == acted_upon_shop`. Any downstream logic in a host application that trusts `WebhookMetadata#shop` to scope data writes, cache updates, session lookups, or triggered actions per tenant can be manipulated cross-tenant by a user who legitimately controls just one shop instance of the app. This satisfies the "cross-tenant access" Critical impact criterion, since it lets one tenant inject data/events attributed to a different, arbitrary tenant, without needing that tenant's access token or the app's `client_secret`.

### Likelihood Explanation
Likelihood is High for any app that: (a) has at least one other unprivileged/installing user who is also a legitimate shop merchant (a normal precondition of any multi-tenant Shopify app), and (b) uses `WebhookMetadata#shop` to key stored state or trigger tenant-scoped actions (the documented intended usage of the field, see `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))`). No leaked secret, TLS interception, or social engineering is required — only ordinary merchant-level access to the attacker's own shop and the ability to send an HTTP POST to the app's public webhook endpoint.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed/verified material, or otherwise cryptographically bind them to the body before trusting `request.shop` — for example, by having the library reject/flag webhooks where the header-derived shop is not corroborated by an app-side registered webhook-to-shop mapping, or by validating that the `shop` claim is consistent with a value obtained through an already-authenticated channel (e.g., cross-checked against a stored subscription/shop registration keyed by `webhook_id`) rather than trusting the raw header alone.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers an event (e.g., `orders/create`) that causes Shopify to deliver a webhook to the app's endpoint.
2. Attacker captures the raw body and `x-shopify-hmac-sha256` value of that delivery (e.g., via their own server logs/proxy, since it is delivered to an endpoint they control as the app's configured callback for their shop, or via a shared testing/staging deployment they control).
3. Attacker re-sends an HTTP POST to the app's public webhook endpoint with the exact same body and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) validates successfully because it only checks the body against the shared `api_secret_key`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-200`) invokes the app's handler with `shop: "victim-shop.myshopify.com"`, causing the attacker's forged/replayed event data to be processed as if it originated from the victim tenant.

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
