### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only. The `shop-domain`, `topic`, `api-version`, and `webhook-id` headers are read directly from attacker-controllable HTTP headers but are never included in the signed material that `Utils::HmacValidator` checks. Because Shopify signs webhooks with the app's single, shop-independent `client_secret`, any merchant who has installed the app can capture one of their own legitimately-signed webhook deliveries and replay it to the app's webhook endpoint with a forged `shop-domain` header pointing at a different (victim) shop. The HMAC still validates (it only covers the body), so the gem hands the forged shop identity to the handler as if it were authentic.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`: [1](#0-0) 

The `hmac` accessor is parsed from the `hmac-sha256` header, while `shop`, `topic`, `api_version`, and `webhook_id` are parsed from separate headers. Crucially, `to_signable_string` returns only `@raw_body`: [2](#0-1) 

`Utils::HmacValidator.validate` computes an HMAC over `to_signable_string` (i.e., the body alone) and compares it against the received `hmac`: [3](#0-2) 

`Webhooks::Registry.process` relies on this validation before trusting `request.shop` and dispatching it (unverified) to the app's handler: [4](#0-3) 

The binding that should hold is: `shop asserted in the authenticated webhook == shop the HMAC was computed for`. In reality, the HMAC is computed by Shopify using the app's shared `client_secret`, independent of which shop the request originated from, and the gem never binds `shop` (or `topic`/`webhook_id`) into the signed payload. Thus:
- Before attack: legitimate webhook for Shop A → body B, header `shop-domain: A`, `hmac = HMAC(secret, B)`.
- Attacker action: replays the exact same body B to the app's webhook endpoint but sets `shop-domain: <victim-shop>`.
- After attack: `hmac` still equals `HMAC(secret, B)` because the signable string never included the shop domain, so `HmacValidator.validate` returns `true`, and `Registry.process` calls the handler with `WebhookMetadata.new(shop: "<victim-shop>", body: ..., topic: ...)` — a forged tenant identity, fully "authenticated" by the gem.

### Impact Explanation
This breaks the tenant-authentication boundary: the app processes a merchant-controlled webhook body under an arbitrary victim shop's identity. Depending on how the host application's webhook handler uses `data.shop` (e.g., to look up/mutate the merchant's stored access token, uninstall state, or other per-tenant records), this enables cross-tenant data corruption or state manipulation without any privileged credentials — only a working installation of the app on the attacker's own store (which is normal, unprivileged usage) is required to obtain one validly-signed webhook body to replay.

### Likelihood Explanation
Any merchant who installs the app receives real, validly-HMAC-signed webhooks from Shopify. Capturing one and replaying it against the public webhook endpoint with a modified `shop-domain` header requires no secret material beyond what Shopify already sent them, and no interaction with the app's `api_secret_key` — an unprivileged, app-installing user can do this from the internet.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the signable content validated against the HMAC, or otherwise cryptographically bind the `shop-domain` header to the signature (e.g., verify it against a shop record established during OAuth, or require it to be reconciled with the topic and body via a signed envelope) before trusting `request.shop` in `Registry.process`.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a legitimate webhook delivery with body `B`, headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: H = HMAC(client_secret, B)`.
2. Attacker POSTs the same body `B` and the same `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "shopify-shop-domain" => "victim.myshopify.com", "shopify-hmac-sha256" => H})` is constructed.
4. `Utils::HmacValidator.validate(request)` computes `HMAC(client_secret, B)` and compares to `H` — validates successfully because `to_signable_string` never touches `shop`.
5. `Webhooks::Registry.process(request)` proceeds and invokes the handler with `shop: "victim.myshopify.com"`, even though the payload never originated from that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
