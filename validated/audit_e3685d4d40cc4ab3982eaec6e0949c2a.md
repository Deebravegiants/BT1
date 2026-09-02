### Title
Webhook `shop-domain`, `topic`, `api-version` and `webhook-id` headers are trusted by `Registry.process` despite not being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook request solely by HMAC-verifying the raw request body, then dispatches the handler using `request.topic`, `request.shop`, `request.api_version`, and `request.webhook_id` — none of which are part of the signed payload.

### Finding Description
The webhook signature check is: [1](#0-0) 

`Utils::HmacValidator.validate(request)` computes the HMAC over `request.to_signable_string`, which for `Webhooks::Request` is defined as only the raw body: [2](#0-1) 

But `topic`, `shop`, `api_version`, and `webhook_id` are all read directly from HTTP headers, which are not part of `to_signable_string` and therefore are not authenticated by the HMAC at all: [3](#0-2) 

`Registry.process` then uses these unauthenticated header values both to select the handler (`@registry[request.topic]`) and to build the `WebhookMetadata` passed to the app's handler, including `shop: request.shop`: [4](#0-3) 

The identity binding that is broken is:
`hmac_valid(body) == true` is treated as proof that `(shop, topic, api_version, webhook_id)` are also authentic, when in fact `hmac_valid` only certifies the body bytes. Since the HMAC secret (`api_secret_key`) is shared across every shop that installs the app, any party that can observe one legitimate webhook delivery (their own store's webhook, which they are fully authorized to receive) obtains a `(body, hmac)` pair that remains valid for that exact body regardless of which `shop-domain` header accompanies the replayed request.

### Impact Explanation
An unprivileged installer of the app (i.e., a user who installs the app on their own shop and thus legitimately receives webhooks for it) can capture one valid `(raw_body, x-shopify-hmac-sha256)` pair from their own webhook deliveries, then replay that exact body/HMAC combination to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header value. `Registry.process` will accept it as valid (HMAC only checks the body) and hand the handler a `WebhookMetadata` claiming the event belongs to a different, victim shop. If the host application trusts `data.shop` to attribute the event to a tenant (as the gem's own documentation instructs: "shop, String - The shop domain of the webhook"), this allows cross-tenant data injection/spoofing — e.g., faking `orders/create`, `app/uninstalled`, or `shop/redact` events against another merchant's tenant record, without ever needing that merchant's credentials.

### Likelihood Explanation
Likelihood is elevated because the attacker only needs their own legitimate app installation (no leaked secret, no privileged account) to obtain a valid signed body, and the webhook endpoint is a public, unauthenticated internet-facing route by design (Shopify itself calls it without any additional authentication). Replaying with a modified `shop-domain` header requires no cryptographic material beyond what the attacker's own tenant already legitimately possesses.

### Recommendation
Bind the tenant-identifying fields to the signature verification, or explicitly document/require that consuming applications must independently verify `data.shop` against their own session store rather than trusting the header. Concretely:
- Include `shop`, `topic`, `api_version`, and `webhook_id` in the signed payload used by `Utils::HmacValidator.validate`, or
- Have `Registry.process` cross-check `request.shop` against a caller-supplied allow-list/expected shop before invoking the handler, and update `docs/usage/webhooks.md` to state clearly that `data.shop` is unauthenticated and must be revalidated by the host application.

### Proof of Concept
1. Install the app on shop `attacker-shop.myshopify.com`; trigger a webhook event (e.g., `orders/create`) and capture the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header `H` that Shopify sends — this pair is valid because `HmacValidator.validate` only signs `B`:
   `OpenSSL.secure_compare(HMAC(api_secret_key, B), H) == true` [5](#0-4) 
2. Replay a forged HTTP POST to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and (optionally) a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because only `B` is checked: [6](#0-5) 
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the host application to process/attribute the event to `victim-shop` even though `victim-shop` never sent it.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
