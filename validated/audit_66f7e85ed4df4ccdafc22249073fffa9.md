### Title
Webhook shop-domain spoofing due to unauthenticated tenant identity in `Webhooks::Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The webhook processing pipeline authenticates only the raw request body via HMAC, but hands the caller-supplied `X-Shopify-Shop-Domain` header — unauthenticated and uncovered by that HMAC — to the application as the trusted tenant identifier. This breaks the identity binding `shop authenticated == shop delivered to handler`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic tie to the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC against `verifiable_query.to_signable_string` (the body only) using the app's `api_secret_key`: [3](#0-2) 

`Registry.process` validates the HMAC and then dispatches the handler using `request.shop` directly, without any check that this shop is the one that actually owns the signed content or was expected to send it: [4](#0-3) 

Because the HMAC binds only `(secret, raw_body)` and not `(secret, raw_body, shop)`, any `(raw_body, hmac)` pair that is valid for one shop is equally valid for a request that claims to be from any other shop — the app's `client_secret` is shared across all installations of the app, so a valid signature obtained from the attacker's own store is transferable to a forged request naming a victim store.

### Impact Explanation
An attacker who has installed the target app on their own (attacker-controlled) Shopify store legitimately receives real, correctly-signed webhook deliveries `(raw_body, hmac)` from Shopify for their own store's events. Because `shop` is not part of the signed content, the attacker can POST that same `raw_body`/`hmac` pair directly to the app's public webhook endpoint while substituting `X-Shopify-Shop-Domain` with a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` calls the registered handler with `WebhookMetadata.shop` set to the victim's domain and `body` fully attacker-controlled (since the attacker chose which of their own webhook events to capture, and the JSON payload structure/fields are attacker-influenced to a meaningful degree, e.g. via metafields/notes on their own store). Any app that uses `data.shop` to select the tenant record to create/update/delete (a very common pattern for webhook handlers, e.g. `orders/create`, `app/uninstalled`, `customers/redact`) will apply attacker-controlled data to another merchant's tenant, i.e., cross-tenant data injection/corruption — impacting confidentiality/integrity across tenant boundaries.

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the app on a store they control (self-serve installable apps satisfy this trivially) and be able to send arbitrary HTTP requests to the app's public webhook endpoint — both are unprivileged-internet-user capabilities. No access token, `client_secret`, or other privileged credential is required.

### Recommendation
Bind the shop identity to the authenticated content: include the `shop` (and ideally `topic`/`webhook_id`) in the HMAC-signable string, or independently verify that the `shop` header corresponds to a shop for which this app currently holds an active, matching webhook subscription/session before invoking the handler, rejecting the request otherwise.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST body and its `X-Shopify-Hmac-Sha256` header — both are validly signed with the app's real `client_secret`.
2. Replay that exact body and HMAC header to the app's public webhook endpoint, but replace `X-Shopify-Shop-Domain` with `victim.myshopify.com`.
3. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) succeeds because it only checks `raw_body` against the HMAC.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the registered handler with `WebhookMetadata.shop == "victim.myshopify.com"` and the attacker-crafted body, even though Shopify never sent this webhook on behalf of `victim.myshopify.com`.

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
