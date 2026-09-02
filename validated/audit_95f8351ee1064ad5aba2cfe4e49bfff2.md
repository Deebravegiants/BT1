This confirms the finding: the gem's own documented API (`docs/usage/webhooks.md`) explicitly tells developers that after `ShopifyAPI::Webhooks::Registry.process` "verifies the request did indeed come from Shopify," the resulting `data.shop` field can be trusted as "The shop domain of the webhook." This is exactly the false binding — the gem asserts a security property (`shop` is authenticated) that its own HMAC check does not provide.

### Title
Webhook shop/topic identity spoofing via HMAC that only covers the body - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated for a given shop once `Utils::HmacValidator.validate` succeeds, and then hands `request.shop` and `request.topic` straight through to the app's handler as trusted `WebhookMetadata`. However the HMAC is computed only over the raw body, never over the `shop-domain` or `topic` headers, so the binding `HMAC_valid(body) == authenticated(shop, topic, body)` does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` and `topic` are read directly from HTTP headers and are never included in the signable string: [2](#0-1) 

`HmacValidator.validate_signature` computes the HMAC using `verifiable_query.to_signable_string` (the body only) and the app's single, shop-independent `Context.api_secret_key`: [3](#0-2) 

`Registry.process` gates only on that body HMAC, then constructs `WebhookMetadata` using the unauthenticated `request.shop` and `request.topic` values and passes it to the app's handler as if the whole tuple were verified: [4](#0-3) 

Because the `api_secret_key` used for the HMAC is the app's single client secret shared across every shop that has installed the app (not a per-shop secret), any legitimately obtained `(raw_body, hmac)` pair — e.g. from a webhook Shopify sent to the attacker's own store, or from a webhook the attacker's shop is entitled to receive — remains a valid HMAC pair regardless of which `shop-domain`/`topic` headers accompany it. An attacker can therefore replay that exact body+HMAC to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header naming a victim shop (and/or a forged `X-Shopify-Topic`), and `HmacValidator.validate` will report success. The equality that should hold — the authenticated shop/topic matches the shop/topic Shopify actually sent this body for — is broken because `shop` and `topic` are "fields acted on but not covered by the HMAC."

### Impact Explanation
This breaks the tenant boundary the gem's own documentation promises: `docs/usage/webhooks.md` states `Registry.process` "will verify the request did indeed come from Shopify" and describes `data.shop` as "The shop domain of the webhook." An app following this documented contract (e.g. dispatching background jobs keyed by `data.shop`, as shown in the doc's own example calling `perform_later(shop_domain: data.shop, ...)`) will process attacker-supplied event content under a victim shop's identity — a cross-tenant data-integrity/spoofing impact, since any shop that installs the app can forge webhook events attributed to any other shop known to it.

### Likelihood Explanation
The prerequisite is only that the attacker controls one legitimate installation of the target app (an unprivileged action — merely installing/using the app on their own shop), which lets them obtain at least one valid `(body, hmac)` pair signed with the app's shared `client_secret`. No access token, no `api_secret_key` leak, and no privileged account is required; the attacker simply modifies unsigned HTTP headers on replay.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signable content (or otherwise cryptographically bind them to the body/signature), or require the caller to separately verify the shop against session/tenant data before trusting `WebhookMetadata#shop`. At minimum, document prominently that only the body's origin is verified and that `shop`/`topic` headers are not authenticated by `HmacValidator`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, obtaining a legitimate webhook delivery with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC_SHA256(app_client_secret, B)`.
2. Attacker POSTs to the app's webhook endpoint with the same raw body `B` and the same `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and any desired `X-Shopify-Topic`.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC_SHA256(app_client_secret, B)` and matches `H` via `OpenSSL.secure_compare`, succeeding — [5](#0-4) .
4. `Registry.process` invokes the app handler with `WebhookMetadata.new(topic: "victim/topic", shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled content as if it originated from Shopify for the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
