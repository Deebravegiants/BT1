### Title
Webhook `shop-domain` and `topic` headers are trusted without HMAC coverage, enabling cross-tenant webhook confusion - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then passes the `shop` (and `topic`) values — taken from HTTP headers that are **not** part of the signed bytes — straight to the app's handler as if they were verified.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` and `topic` are read directly from headers (`shopify-shop-domain`, `shopify-topic`) and are never included in the signable string, so they are excluded from HMAC coverage: [2](#0-1) 

`Registry.process` validates only the HMAC of the body via `HmacValidator.validate(request)` and then constructs `WebhookMetadata` using the unauthenticated `request.shop` and `request.topic`, handing it to the app's handler as trusted, verified data: [3](#0-2) 

The identity binding broken is: `hmac-verified-bytes == request.shop`. In reality, the HMAC only proves `hmac-verified-bytes == raw_body`; `shop` is attacker/network-controlled metadata that rides alongside the signed payload but is never cryptographically bound to it. Since `HmacValidator.compute_signature`/`validate_signature` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) only ever signs `verifiable_query.to_signable_string`, any header outside that string is out of scope of the guarantee the gem's own `process` method implicitly claims to provide (`"Invalid webhook HMAC."` error framing implies the whole request has been authenticated).

### Impact Explanation
An attacker who can capture one valid (raw_body, hmac) pair for shop A's webhook (e.g., via a compromised transport, logging, replay of a webhook the attacker's own store received, or any channel that surfaces the pair) can resubmit that exact body/HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header for shop B. `Registry.process` will accept it — the HMAC still validates against the same secret/body — and will hand the handler a `WebhookMetadata` claiming the data belongs to shop B. Any app that uses `data.shop` to select or write tenant state (the documented purpose of the field) is exposed to cross-tenant data confusion/injection, since the gem itself offers no way to detect that `shop` was not covered by the signature. This matches the "cross-tenant access" impact tier.

### Likelihood Explanation
Exploitation requires obtaining at least one legitimate (body, hmac) pair, which is a lower bar than forging a HMAC (no secret needed) — webhook bodies/HMACs are commonly visible in application logs, proxy logs, or via an attacker's own connected store triggering an identical-shape webhook (e.g., `app/uninstalled` bodies are near-static). The gem provides no header-binding, so every consumer of `Webhooks::Registry.process` inherits this gap unless they add out-of-band shop verification themselves, which is undocumented in this codebase's `lib/` and not enforced anywhere here.

### Recommendation
Bind `shop` (and ideally `topic`, `api_version`, `webhook_id`) into the HMAC-signed material, or otherwise cryptographically tie the header claims to the verified payload before constructing `WebhookMetadata`. At minimum, `Registry.process` should not present `request.shop`/`request.topic` as trusted output of a "validated" request when they are excluded from `to_signable_string`.

### Proof of Concept
1. Attacker legitimately owns/operates `attacker-shop.myshopify.com` and receives a real webhook from Shopify for topic `app/uninstalled` with body `raw_body` and valid header `shopify-hmac-sha256: H`.
2. Attacker resends an HTTP request to the victim app's webhook endpoint with the same `raw_body` and `shopify-hmac-sha256: H`, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` computes `HmacValidator.validate(request)` over `raw_body` only — validation succeeds because the body/HMAC pair is genuinely valid: [4](#0-3) 
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and, trusting the gem's "validated" webhook, performs an action (e.g., de-authorizing/uninstall-cleanup, or writing app data) against `victim-shop`'s tenant record instead of the attacker's own.

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
