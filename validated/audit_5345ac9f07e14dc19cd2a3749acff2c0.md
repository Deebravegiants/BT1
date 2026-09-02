### Title
Webhook shop attribution is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
This is the identity-binding analog of the DAI/`PrizeVault` class of bug: a signature check that guarantees the integrity of *one* field is treated by the caller as if it also guaranteed the integrity of a *different, unrelated* field that travels alongside it. In `PrizeVault`, `permit()`'s signature covered `owner/spender/value/deadline` but the caller assumed DAI's differently-shaped signature covered the same semantics. In this gem, `ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw HTTP body, while the `shop` (and `topic`, `webhook_id`, `api_version`) come from separate, unauthenticated HTTP headers that are never mixed into the HMAC computation.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` calls `validate_signature`, which computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the received `hmac`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw request body — none of the Shopify headers are part of the signed material: [2](#0-1) 

`shop`, `topic`, `webhook_id`, and `api_version` are instead read straight from HTTP headers with no cryptographic binding to the HMAC: [3](#0-2) 

`Registry.process` only checks that the (header-independent) body HMAC is valid, then forwards the unauthenticated `request.shop` straight into the handler's `WebhookMetadata`: [4](#0-3) 

The identity binding that should hold is:
`shop value trusted by the HMAC check` == `shop value the handler attributes the event to`

In this implementation, the left side is actually "no shop value at all" (the HMAC only proves the *body bytes* were MAC'd with `api_secret_key`), while the right side is an attacker-suppliable header. Anything that can produce one valid `(body, hmac)` pair signed by the app's `api_secret_key` can pair that body with an arbitrary `x-shopify-shop-domain` header and still pass `HmacValidator.validate`.

### Impact Explanation
Because a single shared webhook endpoint URL is normally registered to receive events for every shop that installs the app, and the HMAC only authenticates the body (not the sender's identity), an attacker who legitimately installs the app on their own (even free/dev) store can:
1. Trigger or otherwise obtain a genuine webhook delivery for their own store, capturing the exact `(raw_body, x-shopify-hmac-sha256)` pair Shopify signed with the app's real `api_secret_key`.
2. Replay that exact body/HMAC pair directly to the shared webhook endpoint, but with `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) rewritten to any other shop that uses the same app.
3. `HmacValidator.validate` still returns true (body bytes and HMAC still match), so `Registry.process` invokes the handler with `WebhookMetadata#shop` set to the spoofed victim domain and attacker-controlled body content.

Any host application logic that uses `WebhookMetadata#shop` to select per-tenant records, update per-shop state, or key stored credentials will act on attacker-controlled data while believing it originated from the victim tenant — a cross-tenant data-integrity/confusion issue in a multi-tenant SaaS app built on this gem.

### Likelihood Explanation
Medium-to-high for any consumer of `Webhooks::Registry`/`Webhooks::Request` in a multi-tenant app: the attacker needs no leaked credentials or privileged access — only their own ordinary storefront/dev-store install of the target app to obtain one legitimate `(body, hmac)` pair, since the shop identity is never covered by the signature.

### Recommendation
Bind the tenant identity into the signed material the same way DAI's permit needed its own nonce accounted for: verify that the shop asserted in the `x-shopify-shop-domain` header actually corresponds to the webhook's registered destination (e.g., cross-check against the shop associated with the `webhook_id`/subscription, or require the caller to supply and check the expected shop out-of-band) before trusting `WebhookMetadata#shop`. At minimum, `Registry`/`Request` documentation should explicitly warn that `shop`, `topic`, and `webhook_id` are **not** authenticated by the HMAC check and must not be used as a trust boundary without additional verification.

### Proof of Concept
1. Attacker creates their own Shopify dev/trial store and installs the target app (ordinary, unprivileged action).
2. Attacker triggers an event (e.g., `orders/create`) that causes Shopify to POST a webhook to the app's shared endpoint with a body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC_SHA256(api_secret_key, B)` — attacker now knows a valid `(B, H)` pair.
3. Attacker sends their own HTTP request to the same shared webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, still valid per `Request#to_signable_string`/`HmacValidator.validate_signature`), but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` passes HMAC validation and calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)`, as shown in [4](#0-3) , causing the app to attribute attacker-controlled content to the victim tenant.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
