## Title
Webhook shop identity (and topic/webhook_id) is not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic once `Utils::HmacValidator.validate` succeeds, then forwards the `shop`, `topic`, `webhook_id`, and `api_version` values straight from the request headers to the app's handler. The HMAC, however, is computed and verified only over the raw request body — the shop-identifying header is never part of the signed content, so it can be freely substituted by anyone who can produce (or replay) any HMAC-valid body for the shared app secret.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled directly from attacker-reachable HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.hmac` against a signature computed over `to_signable_string`, i.e. the body alone: [3](#0-2) 

`Registry.process` accepts any request whose body-HMAC is valid and then constructs `WebhookMetadata` using the unverified `request.shop`, `request.topic`, and `request.webhook_id`, handing this attacker-controlled identity straight to the app-defined handler: [4](#0-3) 

Because the same `api_secret_key` (the app's single `client_secret`) is used to sign webhooks for every shop that installs the app, any merchant who installs the app can legitimately receive a genuine, HMAC-valid webhook body for their own store (e.g. `orders/create`, `app/uninstalled`, or the mandatory `customers/data_request`/`customers/redact`/`shop/redact` topics). That merchant can then resend the *identical* raw body and HMAC to the app's webhook endpoint while changing only the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header to name a **different, victim shop**. `HmacValidator.validate` still succeeds because it never inspects those headers, and `Registry.process` hands the victim shop's identity, paired with attacker-chosen body content, to the app's handler.

This breaks the identity binding the gem's own API implies: "the shop whose secret validated this HMAC" versus "the shop the handler is told this event belongs to" are not the same value.

### Impact Explanation
This is a cross-tenant integrity/data-injection primitive: an unprivileged app user (one who is only entitled to send events for their own shop) can inject fabricated webhook events attributed to any other shop known to use the app, including privacy-sensitive mandatory topics like `customers/data_request` or `shop/redact`, or business events like `orders/create`/`app/uninstalled` that many apps use to drive state changes (e.g. deactivating a subscription, triggering fulfillment, or deleting merchant data) keyed by the spoofed `shop` value. This matches the "cross-tenant access" impact category.

### Likelihood Explanation
Any developer/merchant who can install the target app (a normal, unprivileged action) can capture one genuine webhook delivery for their own shop and replay it with a modified `shop-domain` header — no access to the app's `client_secret`, TLS interception, or privileged account is required. This makes the attack straightforward once the app is public.

### Recommendation
Bind the shop (and ideally topic/webhook_id) to the signed payload before trusting it — e.g. verify the header-provided shop against the shop associated with the stored/looked-up session or offline access token before acting on the webhook, rather than trusting the `X-Shopify-Shop-Domain` header purely because the body-only HMAC validated. At minimum, document prominently that `request.shop`/`request.topic` are **not** authenticated by `HmacValidator.validate` and must be independently cross-checked by the consuming app against known installed shops.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and lets Shopify deliver a normal webhook (e.g. `orders/create`) to the app's endpoint; attacker captures the raw body `B` and the `X-Shopify-Hmac-Sha256` header value `H` (valid because Shopify signed it with the app's shared secret).
2. Attacker resends the exact same body `B` and header `H` to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain` with `victim.myshopify.com` (and optionally changes `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and matches `H` — validation passes.
4. `Registry.process` dispatches `WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", body: ..., ...)` to the app's handler, which now processes attacker-supplied data as an authentic event from `victim.myshopify.com`.

### Citations

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
