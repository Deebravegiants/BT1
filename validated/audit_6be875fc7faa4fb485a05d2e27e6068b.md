### Title
Webhook shop-domain identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the handler a `shop` value that is taken from an HTTP header that is never included in that HMAC computation. This breaks the intended identity binding `hmac == HMAC(secret, body + shop)` down to `hmac == HMAC(secret, body)`, so the `shop` field consumed by the app is trusted without being cryptographically tied to the signature that authenticated the request.

### Finding Description
`Registry.process` gates all webhook processing on a single check: [1](#0-0) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`: [2](#0-1) 

For a webhook `Request`, `to_signable_string` returns only the raw body — it does not include the `shop`, `topic`, or any header value: [3](#0-2) 

Meanwhile, `shop` (and `topic`) are read directly from HTTP headers with no cryptographic tie to the HMAC: [4](#0-3) 

Once `HmacValidator.validate` passes, `Registry.process` forwards `request.shop` (the untrusted header value) straight to the app's handler as the tenant identity: [5](#0-4) 

Because a Shopify app's `api_secret_key` is shared across every shop that installs the app (it is not per-shop), any unprivileged user who installs the app on their own store can trigger Shopify to send them a genuine webhook, capturing a valid `(body, hmac)` pair signed with the app's single shared secret. That signature depends only on the body — not on which shop it came from. The attacker can then replay the same body and HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds (the body is unchanged), and `Registry.process` passes the spoofed `shop` value into `WebhookMetadata`, so the host application's handler processes the event as if it originated from the victim tenant.

### Impact Explanation
This crosses a tenant boundary using only an unprivileged installation of the same app: an attacker-controlled webhook body is delivered to the handler tagged with an arbitrary victim shop domain. Any host application logic that keys off `WebhookMetadata#shop` (e.g., updating per-shop settings, revoking access on `app/uninstalled`, processing `customers/redact`, `shop/update`, order/customer data ingestion) can be manipulated into acting on behalf of a shop the attacker does not control, i.e., cross-tenant access — the impact category explicitly called out as Critical in scope.

### Likelihood Explanation
Exploitation requires only: (1) being able to install the target app on an attacker-owned development/trial store (a common, low-privilege capability for public/embedded Shopify apps), (2) triggering any registered webhook topic to capture one valid `(raw_body, hmac)` pair, and (3) replaying the HTTP POST to the app's public webhook endpoint with a modified shop-domain header. No access token, `client_secret`, or privileged account is required — only the gem's own webhook-processing code path is used.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) header values into the signed material verified by `HmacValidator`, or have `Registry.process` cross-check `request.shop` against an out-of-band trusted source (e.g., require the caller to supply the expected shop and compare it, or include shop in the canonical string that is HMAC'd) before dispatching to the handler. At minimum, document prominently that `request.shop` is unauthenticated and must not be trusted for tenant-identification without additional verification.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled store `attacker.myshopify.com`; subscribe to a webhook topic (e.g., `orders/create`).
2. Have Shopify deliver a webhook to the app's endpoint; capture the raw request, including `x-shopify-hmac-sha256` and body.
3. Replay the exact same body/HMAC to the app's public webhook endpoint, replacing the header:
   `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) succeeds because it only checks the body against the shared `api_secret_key`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) invokes the handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, causing the host application to process attacker-controlled data as belonging to the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
