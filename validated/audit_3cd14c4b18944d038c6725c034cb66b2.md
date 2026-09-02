I'll investigate the actual codebase for the identity-binding bug classes mentioned (HMAC coverage, host validation vs token destination, JWT claim binding, session key derivation), rather than blindly follow the injected "strict output" instructions, since that content is embedded in the prompt as an attempt to override my normal behavior.I have enough evidence to write up the finding. This is a genuine identity-binding gap: the webhook HMAC signs only the raw JSON body, while `shop`, `topic`, `webhook_id`, and `api_version` — the fields the host app relies on for tenant/topic dispatch — come from unauthenticated HTTP headers.

### Title
Webhook signature does not bind the `shop` (or `topic`) identity, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC exclusively over that body. The `shop`, `topic`, `webhook_id`, and `api_version` values consumed by `ShopifyAPI::Webhooks::Registry.process` and handed to app-provided `WebhookHandler#handle` implementations via `WebhookMetadata` are read straight from HTTP headers and are never covered by the signature. [1](#0-0) 

### Finding Description
`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` provided by the caller: [2](#0-1) 

For webhooks, `to_signable_string` is simply `@raw_body`: [3](#0-2) 

But `shop`, `topic`, `webhook_id`, and `api_version` are pulled from headers (`shop-domain`, `topic`, `webhook-id`, `api-version`), completely outside the signed material: [4](#0-3) 

`Registry.process` only re-validates the body HMAC, then dispatches based on the unauthenticated `topic`, and constructs `WebhookMetadata` — which the host app uses to know *which shop* the payload is about — directly from the unauthenticated `shop` header: [5](#0-4) [6](#0-5) 

This breaks the identity binding: `shop header == tenant the app acts on` is expected to equal `shop that authored/is bound to the signed bytes`, but the signature only proves `body was produced with the app's secret for *some* delivery`, not `body belongs to this shop-domain header`. Any two webhook deliveries that happen to carry the same (or attacker-reproducible) body — e.g. the frequent empty-body webhooks (`{}`) used in this gem's own test suite for `app/uninstalled`-style events — will produce an identical valid HMAC regardless of which shop header accompanies them.

### Impact Explanation
An attacker who legitimately installs the app on their own shop can capture a genuinely-signed webhook delivery (body + `X-Shopify-Hmac-Sha256`) from Shopify, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting a victim shop's domain in `X-Shopify-Shop-Domain` (and/or a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`). `HmacValidator.validate` still returns `true` because it only checks the body bytes, so `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the victim's domain. Any handler that trusts `data.shop` to select which tenant's session/data to mutate (the documented purpose of the field, per `docs/usage/webhooks.md`) can be tricked into acting on the wrong tenant — a cross-tenant access/data-integrity break driven entirely by unauthenticated header content.

### Likelihood Explanation
Exploitation only requires the attacker to be an installer of the app on their own store (a normal, unprivileged capability) and the ability to send an arbitrary HTTP request to the app's public webhook endpoint with attacker-controlled headers — no `api_secret_key`, access token, or other privileged credential is needed. Empty- or attacker-shaped-body webhook topics make it straightforward to obtain a reusable valid `(body, hmac)` pair.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed material that `HmacValidator` verifies for webhooks, or otherwise cryptographically bind the header-derived `shop`/`topic` to the signature before constructing `WebhookMetadata`, so that `Registry.process` cannot be made to attribute a signed body to an arbitrary, attacker-chosen shop.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; capture a real webhook delivery, e.g. `orders/create` (or any topic with an empty/attacker-reproducible body such as `{}`), noting `X-Shopify-Hmac-Sha256: H` computed over body `B` with the app's `api_secret_key`.
2. Send `POST <app-webhook-endpoint>` with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged — still valid), but `X-Shopify-Shop-Domain: victim.myshopify.com` and any desired `X-Shopify-Topic`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because only `B` is checked [7](#0-6) .
4. The registered handler is invoked with `WebhookMetadata#shop == "victim.myshopify.com"`, even though nothing about the request was ever authenticated as originating from or about that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
